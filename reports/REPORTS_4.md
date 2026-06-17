# Laporan Pengembangan Tahap 4 — Cyanix-CLI-Shell (CyanSh)

Dokumen ini menjelaskan implementasi fitur, manajemen proses tingkat rendah, dan penanganan ketahanan sistem yang diselesaikan pada **Tahap 4** pengembangan prototipe **Cyanix-CLI-Shell (CyanSh)**.

---

## Bab 1: Apa yang Sudah Diimplementasikan

Pada Tahap 4, pengembangan difokuskan untuk mengintegrasikan fungsionalitas manajemen proses tingkat rendah pada sistem operasi berbasis POSIX, memperkuat ketahanan masukan terminal, serta menambahkan perintah manajemen file universal:

1. **Validasi Input Panjang Buffer Real-time**:
   Masukan panjang karakter divalidasi langsung secara real-time di dalam loop pembacaan tombol pada fungsi `read_line_interactive()`. Karakter baru akan otomatis diabaikan apabila panjang buffer string masukan telah mencapai 1024 karakter. Proteksi real-time ini juga disematkan pada mekanisme pelengkapan otomatis (Tab dan Right Arrow) serta penempelan clipboard (Ctrl+V) untuk menjamin ketahanan buffer masukan sebelum tombol Enter ditekan.

2. **Validasi Batas Maksimum 64 Argumen Real-time**:
   Sistem secara dinamis menghitung estimasi jumlah token/argumen menggunakan parser real-time setiap kali pengguna mengetik karakter baru atau menempelkan teks. Jika pengetikan karakter baru atau penempelan teks memicu terbentuknya argumen baru yang melebihi batas maksimal 64 argumen, input tersebut akan diabaikan demi menjaga kestabilan alokasi memori sistem.

3. **Fitur Tab-Cycling Autocomplete (Multi-match)**:
   Sistem pelengkapan otomatis (autocomplete) berbasis tombol Tab kini mendukung pemilihan melingkar (cycling):
   - Jika pengguna mengetik sebagian nama folder (misal `cd sys`) lalu menekan Tab, shell mencari seluruh folder yang cocok (misal `System` dan `System32`).
   - Penekanan Tab pertama kali akan langsung melakukan penulisan otomatis pilihan pertama (`System/`). Jika tombol Tab ditekan lagi secara berurutan tanpa mengetik karakter baru, nama sebelumnya dihapus otomatis dan diganti pilihan kedua (`System32/`). Pilihan akan terus berputar secara melingkar (loop/cycle).
   - Status rotasi dikelola oleh state tracker (`current_matches`, `match_index`, `original_prefix`) di dalam `read_line_interactive()` and di-reset seketika jika pengguna mengetik karakter baru, menekan Backspace/Delete, atau tombol Panah.
   - Nama folder terpilih otomatis dibungkus tanda kutip ganda jika mengandung karakter spasi (misal `cd "System Data/"`).

4. **Proteksi Argumen Kosong (Kekurangan Operand)**:
   Sistem pemantauan parameter mendeteksi secara preventif jika pengguna mengetikkan perintah utama saja (`mkdir`, `rm`, `mv`, `cp`, `cat`) tanpa menyertakan objek target. Shell akan menghentikan proses eksekusi dan mencetak informasi kesalahan yang jelas berupa petunjuk panduan sintaks penggunaan yang benar dalam Bahasa Indonesia.

5. **Perintah Bawaan Universal Terintegrasi**:
   * **`dir`**: Menampilkan isi direktori secara alfabetis (folder dulu baru file, case-insensitive). Opsi `-a` menampilkan file hidden (diawali titik `.`). Flag lain mencetak error: `dir: error: flag tidak valid.`. Perintah `ls` dihapus seluruhnya.
   * **`touch` & `mkdir`**: `touch` membuat file kosong baru. `mkdir` membuat direktori/folder baru secara langsung menggunakan `os.makedirs`. Folder dengan nama berakhiran ekstensi titik (seperti `mkdir test.txt`) akan tetap dibuat sebagai direktori/folder.
   * **`cat`**: Membaca dan menampilkan teks berkas UTF-8. Dilengkapi proteksi direktori (`cat: error: [folder] adalah sebuah direktori.`) dan proteksi file tidak ditemukan (`cat: error: [file] tidak ditemukan.`).
   * **`cp`**: Menyalin file (`shutil.copy2`) atau direktori rekursif (`shutil.copytree`) dengan flag `-r`/`-R`. Proteksi jika menyalin folder tanpa flag: `cp: error: [sumber] adalah direktori. Gunakan flag '-r' untuk menyalin folder.`
   * **`mv`**: Memindahkan atau mengubah nama berkas/folder (`shutil.move`) secara langsung tanpa flag `-r`.
   * **`rm`**: Menghapus file (`os.remove`). Untuk folder wajib menggunakan flag `-r`/`-R` (`shutil.rmtree`), jika tanpa flag akan dibatalkan dengan error: `rm: error: [nama_folder] adalah direktori. Gunakan flag '-r' untuk menghapus.`
   * Seluruh perintah di atas ditangani secara aman dengan try-except untuk mencegah crash.

6. **Mekanisme Low-Level Forking & Exec (Tahap 4 POSIX)**:
   Pada platform POSIX, eksekusi perintah eksternal menggunakan manajemen proses tingkat rendah:
   - Shell menduplikasi dirinya menggunakan system call `os.fork()` untuk melahirkan proses anak (*child process*).
   - Di dalam proses anak, ruang memori diganti sepenuhnya dengan program eksternal yang dipanggil beserta argumennya menggunakan keluarga fungsi eksekusi, spesifiknya `os.execvp()`. Jika program eksternal gagal dipanggil atau tidak ditemukan, proses anak keluar secara instan menggunakan `os._exit(127)` untuk mencegah kebocoran eksekusi kode induk oleh anak.
   - Di dalam proses induk (*parent process*), digunakan system call `os.waitpid()` untuk membekukan sementara eksekusi shell utama hingga proses anak selesai berjalan.

7. **Cross-Platform Fallback Mechanism**:
   Karena system call `os.fork()` tidak tersedia pada sistem operasi Windows native, sistem menggunakan deteksi fitur bersyarat `hasattr(os, 'fork')`. Jika berjalan pada Windows, shell akan beralih (*fallback*) secara otomatis dan aman ke eksekusi berbasis modul `subprocess.run()`. Ketika perintah tidak dikenali oleh CMD, program menangkapnya dan mencetak error terstandar: `[perintah] tidak dikenali sebagai perintah internal atau eksternal, program yang dapat dijalankan, atau file batch.`

8. **Manajemen Sinyal & State Terminal**:
   - **State Terminal**: Sebelum memanggil subproses eksternal, mode masukan mentah terminal dinonaktifkan (`disable_raw_mode()`). Setelah proses anak selesai, raw mode terminal dinyalakan kembali secara aman (`enable_raw_mode()`) di dalam blok `finally`.
   - **Manajemen Sinyal**: Saat perintah eksternal sedang berjalan, proses induk mengabaikan sinyal interrupt `SIGINT` (Ctrl+C) menggunakan `signal.SIG_IGN`. Sebaliknya, proses anak mengembalikan handler sinyal tersebut ke default (`signal.SIG_DFL`) agar sinyal Ctrl+C diteruskan langsung untuk menghentikan proses anak tanpa mematikan loop utama shell `CyanSh`.

9. **Dukungan Paste Clipboard via Pintasan Keyboard (Ctrl+V)**:
   Deteksi tombol Ctrl+V (byte `b'\x16'`) mengakses *system clipboard* menggunakan API `ctypes` asli di Windows dengan console window handle, serta `pbpaste` di macOS atau `xclip`/`xsel` di Linux. Teks clipboard disaring dari karakter kontrol kemudian disisipkan pada kursor teks secara real-time dengan tetap menghormati batas maksimum 1024 karakter dan 64 argumen.

---

## Bab 2: Struktur Berkas & Modul yang Diperbarui

Struktur direktori proyek saat ini setelah penyelesaian seluruh tahap pengembangan adalah sebagai berikut:

```text
Cyanix-CLI-Shell/
├── config.py
├── shell.py
├── reports/
│   ├── REPORTS_1.md
│   ├── REPORTS_2.md
│   ├── REPORTS_3.md
│   └── REPORTS_4.md
└── utils/
    ├── __init__.py
    ├── builtins.py
    └── parser.py
```

Peran dari masing-masing berkas yang mengalami modifikasi besar pada tahap ini meliputi:
- **`shell.py`**: Mengandung REPL loop utama, pembacaan input mentah berbasis `getwch()`, penangkapan interupsi kursor, perhitungan lebar visual karakter menggunakan `unicodedata`, pembatasan input real-time 1024 karakter/64 argumen, paste clipboard (Ctrl+V), dan Tab-cycling autocomplete.
- **`utils/builtins.py`**: Menampung logika eksekusi perintah builtin (`cd`, `pwd`, `dir`, `touch`, `mkdir`, `cat`, `cp`, `mv`, `rm`), logika pembelahan proses (`os.fork` + `os.execvp`), penanganan sinkronisasi induk-anak (`os.waitpid`), manajemen state raw mode terminal, serta masking sinyal Ctrl+C (`SIGINT`).
- **`utils/parser.py`**: Melakukan tokenisasi argumen perintah dengan modul `shlex` serta memvalidasi panjang input secara statis untuk mendukung ketahanan sistem (*defense-in-depth*).

---

## Bab 3: Detail Section Penugasan

### A. Capaian
- Pengguna dapat mengeksekusi semua jenis program eksternal bawaan sistem operasi secara aman dengan argumen opsional di platform Unix/POSIX maupun Windows.
- Sinyal Ctrl+C berhasil disalurkan langsung ke subproses tanpa merusak kestabilan memori dan menghentikan proses shell induk.
- Input terproteksi dari glitch visual koordinat kursor terminal meskipun mengandung karakter non-ASCII (seperti huruf mandarin/jepang) atau emoji.
- Validasi batas input 1024 karakter dan batas maksimal 64 argumen bekerja secara real-time sebelum penekanan tombol Enter.
- Pengguna dapat memilih opsi pelengkapan otomatis secara melingkar (Tab-cycling) di mana nama direktori berspasi dibungkus tanda kutip secara otomatis.
- Perintah builtin baru (`touch`, `cat`, `cp`, `mv`, `mkdir`, `rm`) berjalan dengan proteksi keselamatan (try-except) dan kekurangan operand bahasa Indonesia yang seragam.

### B. Progress dan Problem
- **Problem 1**: Sinyal interrupt `SIGINT` (Ctrl+C) secara bawaan akan menghentikan proses Python utama. Ketika menjalankan subproses eksternal, jika pengguna menekan Ctrl+C, shell utama ikut mati.
- **Solusi 1**: Mengatur penanganan sinyal di proses induk agar mengabaikan `SIGINT` (`signal.SIG_IGN`) sesaat sebelum pemanggilan `os.waitpid()`, dan mengembalikannya setelah subproses selesai. Di proses anak, sinyal `SIGINT` dikembalikan ke penanganan default (`signal.SIG_DFL`) agar subproses berhenti saat terinterupsi.
- **Problem 2**: Pemrosesan autocomplete berspasi. Jika nama direktori memiliki spasi seperti `System Data`, setelah ditambahkan ke prompt tanpa tanda kutip, parser shell menganggapnya sebagai dua argumen berbeda.
- **Solusi 2**: Menambahkan pendeteksian spasi pada kata yang berhasil dicocokkan di `get_all_matches()`. Jika ditemukan spasi, nilai pelengkapan otomatis dibungkus dengan tanda kutip ganda (misal `"System Data/"`) sehingga dibaca sebagai satu argumen.
- **Problem 3**: Penanganan clipboard raw mode. Raw mode menonaktifkan penanganan I/O konsol bawaan Windows/Unix, menyebabkan penekanan Ctrl+V tidak melakukan penempelan otomatis, melainkan mengirimkan byte biner `\x16`.
- **Solusi 3**: Menangkap byte `b'\x16'` secara manual di loop input interaktif, lalu mengambil teks clipboard melalui API Ctypes `user32` di Windows atau perintah POSIX, menyaringnya dari karakter kontrol, dan menyisipkannya langsung ke buffer input secara real-time.

### C. Testing Skenario

| No | Skenario Uji Coba | Langkah Uji | Hasil yang Diharapkan | Status |
|----|---|---|---|---|
| 1 | Uji Tab-Cycling Autocomplete | Mengetik `cd sys` lalu menekan `Tab` beberapa kali tanpa mengetik karakter baru | Input otomatis berganti antara `cd System/` dan `cd System32/` secara berputar/melingkar | Lolos |
| 2 | Uji Pelanggaran Batas 64 Argumen | Memasukkan perintah yang terdiri atas 65 argumen angka terpisah spasi | Karakter yang memicu pembentukan argumen ke-65 akan diabaikan secara real-time dan tidak dapat diketik | Lolos |
| 3 | Uji Kekurangan Operand Protektif | Mengetik perintah `mkdir`, `rm`, atau `cp` tanpa argumen apa pun | Shell membatalkan proses dan mencetak error petunjuk penggunaan yang sesuai (e.g., `cynix: mkdir: kekurangan operand. Penggunaan: mkdir [nama_folder]`) | Lolos |
| 4 | Uji Pembuatan Direktori `mkdir` | Menjalankan `mkdir direktori_uji` dan `mkdir folder_uji.txt` | Terbentuk dua direktori bernama `direktori_uji` dan `folder_uji.txt` | Lolos |
| 5 | Uji Interupsi Foreground Process | Menjalankan subproses eksternal (e.g. `ping 127.0.0.1 -n 100`) lalu menekan Ctrl+C | Subproses berhenti seketika dan shell induk kembali menampilkan prompt baru tanpa menghentikan REPL | Lolos |

### D. Contoh Penggunaan

Simulasi visual keluaran pada terminal saat pengujian perintah file universal Tahap 4:

```text
Muh Daffa@Lenovo-L380-Yoga CyanixOS D:/04_Dev
$ mkdir
cynix: mkdir: kekurangan operand. Penggunaan: mkdir [nama_folder]

Muh Daffa@Lenovo-L380-Yoga CyanixOS D:/04_Dev
$ mkdir folder_demo.txt

Muh Daffa@Lenovo-L380-Yoga CyanixOS D:/04_Dev
$ dir

    Directory: D:\04_Dev

LastWriteTime             Length Name
-------------             ------ ----
6/17/2026   15:40 PM             folder_demo.txt

Muh Daffa@Lenovo-L380-Yoga CyanixOS D:/04_Dev
$ rm folder_demo.txt
rm: error: folder_demo.txt adalah direktori. Gunakan flag '-r' untuk menghapus.

Muh Daffa@Lenovo-L380-Yoga CyanixOS D:/04_Dev
$ rm -r folder_demo.txt

Muh Daffa@Lenovo-L380-Yoga CyanixOS D:/04_Dev
$ ping 127.0.0.1
Pinging 127.0.0.1 with 32 bytes of data:
Reply from 127.0.0.1: bytes=32 time<1ms TTL=128
Control-C
Muh Daffa@Lenovo-L380-Yoga CyanixOS D:/04_Dev
$ 
```

### E. Tahap Lanjutan
Pada tahap berikutnya (Tahap 5), fokus pengembangan adalah mengimplementasikan fitur *I/O Redirection* menggunakan operator `>` dan `<` berbasis `os.dup2()`, penyusunan saluran komunikasi antar-proses (*Piping* dengan operator `|` menggunakan `os.pipe()`), dan perluasan pustaka perintah bawaan.
