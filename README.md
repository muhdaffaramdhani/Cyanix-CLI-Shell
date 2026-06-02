# Cynix-CLI-Shell (CyanSh)

Cynix-CLI-Shell (CyanSh) adalah implementasi shell kustom interaktif berbasis CLI yang terinspirasi dari arsitektur konsep **Cyanix OS** — sistem operasi mikrokernel yang dikembangkan oleh Kelompok 7. Proyek ini dibangun untuk mendemonstrasikan prinsip-prinsip sistem operasi seperti manajemen proses, tokenisasi instruksi, dan modularitas sistem.

Tugas ini disusun untuk memenuhi ujian akhir semester (UAS) mata kuliah **Sistem Operasi**.

---

## 👥 Kelompok 7 — Ilmu Komputer 2024 A

| Nama Anggota | NIM | peran / Kontribusi |
|---|---|---|
| **Fujiono Nur Ikhsan** | 1313624008 | Pengembangan Arsitektur & Core Engine |
| **Nadine Alysha Maheswari** | 1313624009 | Parser & Tokenization Engine |
| **Muhammad Daffa Ramdhani** | 1313624025 | REPL System & Terminal Handlers |
| **Fathya Khairani R** | 1313624056 | UI Aesthetics & System Info Design |

* **Dosen Pengampu:** Ari Hendarno, M.Kom  
* **Instansi:** Universitas Negeri Jakarta  

---

## ✨ Fitur yang Sudah Diimplementasikan

### 1. Tahap 0 — Splash Screen & Boot Banner
* Tampilan visual logo ASCII `CYANIX OS` yang estetis dengan kode warna ANSI True Color (Cyan `#13AFD7`).
* Penyelarasan kolom informasi kontributor yang rapi dan sejajar.
* Konfigurasi terminal otomatis untuk mendukung karakter Unicode UTF-8 dan ANSI Escape Codes di Windows dan Unix.

### 2. Tahap 1 — Membangun REPL (Read-Evaluate-Print Loop)
* Loop interaktif yang terus berjalan menerima perintah pengguna dengan prompt kustom `user@cynix:~$`.
* Keluar dari program secara aman menggunakan perintah `exit` atau sinyal EOF (`Ctrl+D`).
* Penanganan interupsi sinyal `Ctrl+C` agar tidak menghentikan shell secara tidak sengaja.

### 3. Tahap 2 — Parsing Perintah (Command Tokenization)
* Modul parser kustom terisolasi di dalam `utils/parser.py`.
* Melakukan tokenisasi berdasarkan pemisah spasi (` `) dengan pembersihan otomatis spasi berlebih.
* Validasi batas aman input (maksimal 1024 karakter) untuk mencegah buffer overflow atau penyalahgunaan memori.
* Validasi batas jumlah token argumen (maksimal 64 argumen) dengan format pesan kesalahan yang informatif (`cynix: error: too many arguments (max 64)`).

---

## 📁 Struktur Proyek

```text
Cyanix-CLI-Shell/
│
├── shell.py              # Entry Point: Main REPL Loop & Splash Screen
│
├── utils/
│   ├── __init__.py       # Module Exporter
│   └── parser.py         # Parsing & Tokenization (Tahap 2)
│
├── commands/
│   ├── __init__.py
│   ├── builtin.py        # Penyiapan untuk Perintah Built-in (Tahap 3)
│   ├── external.py       # Penyiapan untuk Perintah Eksternal (Tahap 4)
│   └── cyanix_spec.py    # Ekstensi simulasi Cyanix OS
│
├── .gitignore            # Konfigurasi pengabaian file Git
└── README.md             # Dokumentasi proyek
```

---

## 🚀 Cara Menjalankan

### Prasyarat
* Python 3.8 atau versi yang lebih baru.

### Langkah-langkah
1. Klon repositori ini (atau buka direktori proyek):
   ```bash
   git clone https://github.com/muhdaffaramdhani/Cyanix-CLI-Shell.git
   cd Cyanix-CLI-Shell
   ```
2. Jalankan program shell:
   ```bash
   python shell.py
   ```

---

## 🛠️ Rencana Pengembangan Selanjutnya
* **Tahap 3**: Implementasi built-in commands kustom seperti `cd` dan `pwd`.
* **Tahap 4**: Sistem Forking dan eksekusi perintah eksternal menggunakan pustaka OS (`os.fork()` / `subprocess`).
* **Tahap 5**: Mekanisme Piping (`|`) dan Redirection (`>`, `<`).
* **Tahap 6**: Error handling menyeluruh dan stress testing sistem.
