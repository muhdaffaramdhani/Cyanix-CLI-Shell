# Cyanix-CLI-Shell (CyanSh)

Cyanix-CLI-Shell (CyanSh) adalah implementasi **custom shell interaktif** yang dikembangkan sebagai representasi antarmuka baris perintah (*command line interface*) untuk konsep sistem operasi **Cyanix OS** berbasis microkernel.

Tugas ini disusun untuk memenuhi ujian akhir semester (UAS) mata kuliah **Sistem Operasi**.

## Kelompok 7 — Ilmu Komputer 2024 A

| Nama Anggota | NIM |
|---|---|
| **Fujiono Nur Ikhsan** | 1313624008 |
| **Nadine Alysha Maheswari** | 1313624009 |
| **Muhammad Daffa Ramdhani** | 1313624025 |
| **Fathya Khairani R** | 1313624056 |

* **Dosen Pengampu:** Ari Hendarno, M.Kom
* **Instansi:** Universitas Negeri Jakarta

## Fitur Utama (Fungsionalitas Shell)

Shell ini dikembangkan secara modular dan aman, mendukung penanganan masukan interaktif raw mode, dan mencakup fitur-fitur berikut:

### 1. Perintah Bawaan Universal (Built-in Commands)

* `cd [path]` & `cd ..`: Berpindah direktori kerja aktif secara dinamis.
* **Drive Switch Shortcuts (Windows)**: Berpindah partisi drive secara instan hanya dengan mengetik huruf drive diikuti titik dua (contoh: `c:` atau `d:`).
* `pwd`: Menampilkan path absolut direktori kerja aktif saat ini.
* `dir` & `dir -a`: Menampilkan isi direktori secara alfabetis (folder dulu baru file, case-insensitive). Opsi `-a` digunakan untuk menyertakan file hidden (berawalan titik `.`).
* `touch [nama_file]`: Membuat file kosong baru secara eksplisit.
* `mkdir [nama_folder]`: Membuat direktori/folder baru secara langsung menggunakan `os.makedirs`. Nama folder yang menggunakan titik (misal `folder.txt`) akan tetap dibuat sebagai folder.
* `cat [nama_file.txt]`: Membaca dan menampilkan isi teks berkas UTF-8 dengan aman.
* `cp [sumber] [tujuan]` & `cp -r [sumber] [tujuan]`: Menyalin file biasa atau direktori secara rekursif (wajib menyertakan `-r` untuk folder).
* `mv [sumber] [tujuan]`: Memindahkan atau mengubah nama berkas/folder secara langsung tanpa memerlukan opsi khusus.
* `rm [file]` & `rm -r [folder]`: Menghapus berkas atau folder secara aman. Penghapusan direktori wajib menyertakan flag `-r` agar tidak memicu pembatalan dan pesan error.
* `cls` / `clear`: Membersihkan antarmuka layar terminal.
* `help`: Menampilkan daftar perintah bawaan lengkap beserta penjelasannya.
* `exit`: Keluar dari sesi shell secara bersih.

### 2. Keamanan Input Real-time & Proteksi Buffer

* **Proteksi 1024 Karakter & 64 Argumen**: Masukan dibatasi secara real-time langsung di loop input interaktif sebelum penekanan tombol Enter.
* **Proteksi Kekurangan Operand (Missing Operand)**: Menampilkan pesan kesalahan informatif dan panduan penggunaan ketika argumen wajib tidak disertakan.
* **Toleransi Kesalahan Tanda Kutip**: Mencegah crash jika masukan tidak memiliki tanda kutip penutup, mengembalikan pesan kesalahan: `cynix: error: tidak ada tanda kutip penutup`.

### 3. Eksekusi Subproses Forking & Cross-Platform Fallback

* **UNIX Fork & Exec**: Pada OS POSIX, shell menduplikasi proses menggunakan `os.fork()`, mengeksekusi biner eksternal dengan `os.execvp()`, dan menunggu proses selesai dengan `os.waitpid()`. Sinyal interupsi (Ctrl+C) dialirkan ke subproses foreground tanpa mematikan REPL induk.
* **Windows Fallback**: Mengalihkan pemanggilan subproses eksternal ke modul `subprocess` secara aman jika berjalan pada OS Windows. Jika program eksternal tidak ditemukan, akan dicetak error: `'[perintah]' tidak dikenali sebagai perintah internal atau eksternal...`

## Struktur Proyek

```plaintext
Cyanix-CLI-Shell/
│
├── shell.py              # Entry Point: REPL Loop, Key Reader & Interactive Logic
├── config.py             # Konfigurasi: Splash Screen Banner & Terminal States Toggles
│
├── reports/              # Folder Laporan Pengembangan
│   ├── REPORTS_1.md      # Laporan Tahap 1: Dasar REPL Loop
│   ├── REPORTS_2.md      # Laporan Tahap 2: Tokenisasi & Validasi Input
│   ├── REPORTS_3.md      # Laporan Tahap 3: Built-in cd/pwd/dir
│   └── REPORTS_4.md      # Laporan Tahap 4: Forking, cp/mv/cat/touch/mkdir/rm
│
├── utils/
│   ├── __init__.py       # Module Exporter
│   ├── builtins.py       # Handlers Perintah Builtin & Eksekusi Subproses (Fork/Exec)
│   └── parser.py         # Tokenisasi Input & Penanganan Batas Keamanan
│
├── .gitignore            # Konfigurasi Git
└── README.md             # Dokumentasi proyek
```

## Cara Menjalankan

### Prasyarat

* Python 3.8 atau versi yang lebih baru terinstal pada sistem.

### Langkah-langkah

1. Masuk ke direktori proyek:
   ```bash
   cd Cyanix-CLI-Shell
   ```
2. Jalankan program shell biasa:
   ```bash
   python shell.py
   ```
3. Jalankan program shell dalam Mode Debug (menampilkan tokenisasi argumen):
   ```bash
   python shell.py --debug
   ```
