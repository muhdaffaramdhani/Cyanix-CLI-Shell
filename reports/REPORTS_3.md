# Laporan Pengembangan Tahap 3 — Cyanix-CLI-Shell (CyanSh)

Dokumen ini menjelaskan implementasi fitur, manajemen konfigurasi, dan penambahan perintah internal bawaan (*built-in*) dasar yang diselesaikan pada **Tahap 3** pengembangan prototipe **Cyanix-CLI-Shell (CyanSh)**.

---

## Bab 1: Apa yang Sudah Diimplementasikan

Pada Tahap 3, pengembangan diarahkan untuk melengkapi shell dengan serangkaian perintah internal dasar yang berjalan langsung di atas memori proses utama shell (tanpa *forking*), serta menata tata letak program:

1. **Pemisahan Konfigurasi `config.py`**:
   Mengekstrak skema warna ANSI True Color, informasi metadata OS, lisensi, kontributor kelompok, serta inisialisasi visual *splash screen* terminal ke dalam berkas konfigurasi tersendiri agar kode lebih bersih dan terorganisasi.

2. **Implementasi Perintah Built-in Wajib**:
   - **`cd <direktori>`**: Berfungsi memindahkan lokasi direktori aktif shell utama menggunakan system call `os.chdir()`. Menangani error perizinan dan ketiadaan direktori secara aman.
   - **`pwd`**: Berfungsi membaca dan mencetak path absolut direktori kerja aktif saat ini menggunakan system call `os.getcwd()`.

3. **Perintah Penjelajah Direktori Kustom `dir`**:
   Menampilkan isi dari direktori terurut berdasarkan urutan alfabetis (tidak sensitif kapital), dengan mendahulukan kelompok direktori/folder terlebih dahulu kemudian berkas (*files*). Layout kolom informasi didesain menyerupai format keluaran PowerShell (`LastWriteTime`, `Length`, `Name`). File hidden (yang diawali karakter titik `.`) disembunyikan secara default.

4. **Shortcut Perpindahan Drive Windows**:
   Mendukung pergantian partisi drive penyimpanan di Windows secara cepat dengan mengetik nama drive diakhiri tanda titik dua (contoh: `d:` atau `c:`), yang secara internal diterjemahkan ke pemanggilan `os.chdir(drive + "/")`.

5. **Perintah Built-in Utilitas**:
   Menyediakan perintah utilitas tambahan seperti `help` (menu panduan), `cls`/`clear` (menghapus antarmuka layar terminal), dan `debug` (menyalakan/mematikan log tokenisasi argumen).

---

## Bab 2: Struktur Berkas & Modul

Pada Tahap 3, arsitektur modul diperluas untuk mengakomodasi pemisahan perintah bawaan dan data konfigurasi:

```text
Cyanix-CLI-Shell/
├── config.py
├── shell.py
└── utils/
    ├── __init__.py
    ├── builtins.py
    └── parser.py
```

- **`config.py`**: Berkas pusat konfigurasi warna, logo ASCII, informasi kontributor, serta penyiapan mode raw dan pengaturan console mode terminal.
- **`shell.py`**: Mengontrol interaksi input karakter, pembacaan masukan baris interaktif, pelabelan warna prompt, dan pemrosesan utama.
- **`utils/builtins.py`**: Modul handler baru khusus untuk menampung seluruh implementasi fungsi-fungsi perintah builtin shell.
- **`utils/parser.py`**: Modul yang melakukan tokenisasi perintah masukan.
- **`utils/__init__.py`**: Eksportir modular untuk utilitas parsing dan built-in.

---

## Bab 3: Detail Section Penugasan

### A. Capaian
- Pengguna dapat bernavigasi di dalam sistem file hos menggunakan perintah `cd` secara relatif maupun absolut secara aman.
- Lokasi direktori aktif pada prompt diperbarui secara dinamis pasca pemanggilan `cd`.
- Menampilkan visualisasi isi direktori yang rapi dan terstruktur rapi lewat perintah `dir` kustom (PowerShell format).
- Modul konfigurasi visual berhasil membedakan skema warna terminal untuk meningkatkan kualitas pengalaman pengguna (*User Experience*).

### B. Progress dan Problem
- **Problem**: Pada terminal Windows native, karakter warna ANSI escape code seringkali tidak terjemahkan secara visual dan malah tercetak sebagai string mentah yang merusak tampilan terminal.
- **Solusi**: Menggunakan pustaka internal `ctypes` untuk memanggil fungsi API Windows kernel32 `SetConsoleMode` untuk mengaktifkan fitur pemrosesan Virtual Terminal (`ENABLE_VIRTUAL_TERMINAL_PROCESSING` dengan bitmask `7`) di dalam fungsi `setup_terminal()`.

### C. Testing Skenario

| No | Skenario Uji Coba | Langkah Uji | Hasil yang Diharapkan | Status |
|----|---|---|---|---|
| 1 | Perpindahan Direktori Aktif | Mengetik `cd ..` kemudian memeriksa prompt kerja | Lokasi direktori naik satu tingkat ke atas, dan teks prompt ter-render dengan nama direktori baru | Lolos |
| 2 | Menampilkan Isi Direktori | Mengetik `dir` di dalam direktori kerja aktif | Menampilkan daftar folder (terurut A-Z) kemudian daftar file (terurut A-Z) lengkap dengan ukuran dan waktu modifikasi terakhir | Lolos |
| 3 | Pengalihan Partisi Drive (Windows) | Mengetik `D:` pada prompt | Direktori aktif langsung dialihkan ke partisi drive D secara otomatis | Lolos |

### D. Contoh Penggunaan

Simulasi visual keluaran pada terminal saat pengoperasian perintah built-in Tahap 3:

```text
Muh Daffa@Lenovo-L380-Yoga CyanixOS D:/04_Dev
$ pwd
D:\04_Dev

Muh Daffa@Lenovo-L380-Yoga CyanixOS D:/04_Dev
$ dir

    Directory: D:\04_Dev

LastWriteTime             Length Name
-------------             ------ ----
6/17/2026   13:24 PM             Main
6/17/2026   13:25 PM       2514  REPORTS_3.md

Muh Daffa@Lenovo-L380-Yoga CyanixOS D:/04_Dev
$ 
```

### E. Tahap Lanjutan
Pada tahap berikutnya (Tahap 4), fokus pengembangan adalah mengimplementasikan forking proses tingkat rendah (`os.fork`) untuk eksekusi program biner eksternal hos (seperti `ls`, `mkdir` asli OS), penanganan sinkronisasi proses induk-anak (`os.waitpid`), integrasi sinyal interupsi keyboard (Ctrl+C), dan proteksi terminal raw mode, serta melengkapi perintah utilitas file universal (`cp`, `mv`, `cat`, `touch`, `rm`).
