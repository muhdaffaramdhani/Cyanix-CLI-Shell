# Cynix-CLI-Shell (CyanSh)

Cynix-CLI-Shell (CyanSh) adalah implementasi **custom shell interaktif** yang dikembangkan sebagai representasi antarmuka baris perintah (*command line interface*) untuk konsep sistem operasi **Cyanix OS** berbasis microkernel.

Tugas ini disusun untuk memenuhi ujian akhir semester (UAS) mata kuliah **Sistem Operasi**.

---

## Kelompok 7 — Ilmu Komputer 2024 A

| Nama Anggota | NIM |
|---|---|
| **Fujiono Nur Ikhsan** | 1313624008 |
| **Nadine Alysha Maheswari** | 1313624009 |
| **Muhammad Daffa Ramdhani** | 1313624025 |
| **Fathya Khairani R** | 1313624056 |

* **Dosen Pengampu:** Ari Hendarno, M.Kom  
* **Instansi:** Universitas Negeri Jakarta  

---

## Fitur Utama (Fungsionalitas Shell)

Shell ini dapat menerima input perintah dari pengguna, melakukan pemrosesan argumen, dan menjalankan beberapa fungsionalitas berikut:

### 1. Perintah Bawaan (Builtin Commands)
- **`cd [path]` & `cd ..`**: Berpindah direktori secara dinamis.
- **Drive Switch Shortcuts**: Memungkinkan perpindahan drive secara instan di Windows hanya dengan mengetik huruf drive diikuti titik dua (contoh: `c:` atau `d:`).
- **`pwd`**: Menampilkan path lengkap direktori kerja aktif saat ini.
- **`dir`**: Menampilkan daftar isi direktori aktif (kolom: `LastWriteTime`, `Length`, `Name`) terurut alfabetis dengan mendahulukan folder lalu file.
- **`cls` / `clear`**: Membersihkan layar konsol.
- **`help`**: Menampilkan daftar perintah bawaan yang tersedia.
- **`exit`**: Keluar dari program shell secara bersih.

### 2. Mode Analisis Token (Debug Mode)
- Menjalankan shell dengan argumen `--debug` akan menampilkan hasil tokenisasi argumen perintah sebelum dieksekusi. Contoh:
  `cd "Sistem Operasi/"` akan dipecah menjadi:
  - `args[0] = "cd"`
  - `args[1] = "Sistem Operasi/"`

---

## Struktur Proyek

```text
Cyanix-CLI-Shell/
│
├── shell.py              # Entry Point: REPL Loop, Key Reader & Interactive Logic
├── config.py             # Konfigurasi: Splash Screen Banner & Terminal States Toggles
│
├── utils/
│   ├── __init__.py       # Module Exporter
│   ├── builtins.py       # Handlers Perintah Builtin & Eksekusi Subproses
│   └── parser.py         # Tokenisasi Input & Penanganan Batas Keamanan
│
├── .gitignore            # Konfigurasi Git
└── README.md             # Dokumentasi proyek
```

---

## Cara Menjalankan

### Prasyarat
- Python 3.8 atau versi yang lebih baru terinstal pada sistem.

### Langkah-langkah
1. Masuk ke direktori proyek:
   ```bash
   cd Cyanix-CLI-Shell
   ```
2. Jalankan program shell biasa:
   ```bash
   python shell.py
   ```
3. Jalankan program shell dalam Mode Debug:
   ```bash
   python shell.py --debug
   ```