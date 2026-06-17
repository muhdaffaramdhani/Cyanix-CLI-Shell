# Laporan Pengembangan Tahap 4 — Cyanix-CLI-Shell (CyanSh)

Dokumen ini menjelaskan implementasi fitur, manajemen proses tingkat rendah, dan penanganan ketahanan sistem yang diselesaikan pada **Tahap 4** pengembangan prototipe **Cyanix-CLI-Shell (CyanSh)**.

---

## Bab 1: Apa yang Sudah Diimplementasikan

1. **Validasi Input Panjang Buffer Real-time**:
   Masukan panjang karakter divalidasi langsung secara real-time di dalam loop pembacaan tombol pada fungsi `read_line_interactive()`. Karakter baru akan otomatis diabaikan apabila panjang buffer string masukan telah mencapai 1024 karakter.

2. **Validasi Batas Maksimum 64 Argumen Real-time**:
   Sistem secara dinamis menghitung estimasi jumlah token/argumen menggunakan parser real-time setiap kali pengguna mengetik karakter baru atau menempelkan teks. Jika pengetikan karakter baru atau penempelan teks memicu terbentuknya argumen baru yang melebihi batas maksimal 64 argumen, input tersebut akan diabaikan demi menjaga kestabilan alokasi memori sistem.

3. **Proteksi Argumen Kosong (Kekurangan Operand)**:
   Sistem pemantauan parameter mendeteksi secara preventif jika pengguna mengetikkan perintah utama saja (`mkdir`, `rm`, `mv`, `cp`, `cat`) tanpa menyertakan objek target. Shell akan menghentikan proses eksekusi dan mencetak informasi kesalahan yang jelas berupa petunjuk panduan sintaks penggunaan yang benar.

4. **Perintah Bawaan Universal Terintegrasi**:
   * **`dir`**: Menampilkan isi direktori secara alfabetis (folder dulu baru file, case-insensitive). Opsi `-a` menampilkan file hidden (diawali titik `.`). Flag lain mencetak error: `dir: error: flag tidak valid.`. Perintah `ls` dihapus seluruhnya.
   * **`touch` & `mkdir`**: `touch` membuat file kosong baru. `mkdir` membuat direktori/folder baru secara langsung menggunakan `os.makedirs`. Folder dengan nama berakhiran ekstensi titik (seperti `mkdir test.txt`) akan tetap dibuat sebagai direktori/folder.
   * **`cat`**: Membaca dan menampilkan teks berkas UTF-8. Dilengkapi proteksi direktori (`cat: error: [folder] adalah sebuah direktori.`) dan proteksi file tidak ditemukan (`cat: error: [file] tidak ditemukan.`).
   * **`cp`**: Menyalin file (`shutil.copy2`) atau direktori rekursif (`shutil.copytree`) dengan flag `-r`. Proteksi jika menyalin folder tanpa flag: `cp: error: [sumber] adalah direktori. Gunakan flag '-r' untuk menyalin folder.`
   * **`mv`**: Memindahkan atau mengubah nama berkas/folder (`shutil.move`) secara langsung tanpa flag `-r`.
   * **`rm`**: Menghapus file (`os.remove`). Untuk folder wajib menggunakan flag `-r` (`shutil.rmtree`), jika tanpa flag akan dibatalkan dengan error: `rm: error: [nama_folder] adalah direktori. Gunakan flag '-r' untuk menghapus.`
   * Seluruh perintah di atas ditangani secara aman dengan try-except untuk mencegah crash.

5. **Mekanisme Fork & Exec**:
   Pada platform POSIX, eksekusi perintah eksternal menggunakan manajemen proses tingkat rendah:
   - Shell menduplikasi dirinya menggunakan system call `os.fork()` untuk melahirkan proses anak (*child process*).
   - Di dalam proses anak, ruang memori diganti sepenuhnya dengan program eksternal yang dipanggil beserta argumennya menggunakan keluarga fungsi eksekusi, spesifiknya `os.execvp()`. Jika program eksternal gagal dipanggil atau tidak ditemukan, proses anak keluar secara instan menggunakan `os._exit(127)` untuk mencegah kebocoran eksekusi kode induk oleh anak.
   - Di dalam proses induk (*parent process*), digunakan system call `os.waitpid()` untuk membekukan sementara eksekusi shell utama hingga proses anak selesai berjalan.

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
- **`shell.py`**: Mengandung REPL loop utama, pembacaan input mentah berbasis `getwch()`, penangkapan interupsi kursor, perhitungan lebar visual karakter menggunakan `unicodedata`, pembatasan input real-time 1024 karakter/64 argumen.
- **`utils/builtins.py`**: Menampung logika eksekusi perintah builtin (`cd`, `pwd`, `dir`, `touch`, `mkdir`, `cat`, `cp`, `mv`, `rm`), logika pembelahan proses (`os.fork` + `os.execvp`), penanganan sinkronisasi induk-anak (`os.waitpid`).
- **`utils/parser.py`**: Melakukan tokenisasi argumen perintah dengan modul `shlex` serta memvalidasi panjang input secara statis untuk mendukung ketahanan sistem (*defense-in-depth*).

---

## Bab 3: Tahap Lanjutan
Pada tahap berikutnya (Tahap 5), fokus pengembangan adalah mengimplementasikan fitur *I/O Redirection* menggunakan operator `>` dan `<` berbasis `os.dup2()`, penyusunan saluran komunikasi antar-proses (*Piping* dengan operator `|` menggunakan `os.pipe()`), dan perluasan pustaka perintah bawaan.