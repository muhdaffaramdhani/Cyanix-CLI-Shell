# Laporan Pengembangan Tahap 5 — Cyanix-CLI-Shell (CyanSh)

Dokumen ini menjelaskan implementasi fitur tingkat lanjut, modul pemrosesan data, manajemen I/O tingkat rendah, komunikasi antar-proses, dan perbaikan kompatibilitas sistem operasi yang diselesaikan pada **Tahap 5** pengembangan prototipe **Cyanix-CLI-Shell (CyanSh)**.

---

## Bab 1: Apa yang Sudah Diimplementasikan

1. **Perintah Built-in Baru: `grep` (Pure Python)**:
   * Menambahkan perintah pencarian string `grep` yang diimplementasikan secara mandiri menggunakan pustaka murni Python agar dapat berjalan secara lintas-platform (cross-platform) di Windows maupun UNIX/macOS tanpa ketergantungan binary eksternal.
   * Mendukung fitur pencarian:
     * **Pencarian dasar**: `grep "pattern" namafile.ext`
     * **Case-insensitive (`-i`)**: Pencarian teks tanpa memedulikan huruf besar/kecil.
     * **Recursive (`-r` atau `-R`)**: Pencarian pattern secara rekursif di semua berkas dalam direktori dan subdirektori.
     * **Line Number (`-n`)**: Menampilkan nomor baris penemuan string.
     * **Standard Input (stdin) Support**: Membaca otomatis dari `sys.stdin` jika argumen berkas tidak diberikan, memungkinkannya dirangkai di dalam pipa (*piping*).
   * Dilengkapi penanganan exception berkas binary/tak terbaca secara aman (`errors='ignore'`) dan hak akses ditolak (`PermissionError`).

2. **Manipulasi I/O Redirection (`>` dan `<`)**:
   * **Output Redirection (`>`)**: Mengarahkan output standar (stdout) perintah ke dalam berkas. Pada sistem POSIX, ini memanfaatkan system call tingkat rendah `os.open` dan menduplikasinya menggunakan `os.dup2(fd_file, 1)`.
   * **Input Redirection (`<`)**: Mengambil input standar (stdin) perintah dari berkas teks menggunakan `os.dup2(fd_file, 0)`.
   * **Windows Fallback**: Mengarahkan input/output secara logis dengan parameter `stdin` dan `stdout` pada `subprocess.Popen` untuk perintah eksternal, serta manipulasi objek stream `sys.stdin`/`sys.stdout` sementara menggunakan `io.StringIO` untuk perintah built-in.

3. **Implementasi Piping (`|`)**:
   * **POSIX (System Call Pipeline)**:
     * Aliran data dari proses kiri ke kanan dihubungkan menggunakan deskriptor pipa yang dibuat via `os.pipe()`.
     * Setiap tahapan perintah dalam pipa dilahirkan melalui proses anak (`os.fork()`).
     * Menggunakan `os.dup2()` untuk menyambungkan output standar (stdout/`1`) child process kiri ke ujung tulis pipa (*write-end*), dan input standar (stdin/`0`) child process kanan ke ujung baca pipa (*read-end*).
     * Parent process menutup seluruh deskriptor pipa miliknya agar proses tidak menggantung, dan menggunakan `os.waitpid()` untuk menunggu sinkronisasi seluruh child process.
   * **Windows Fallback (Sekuensial In-Memory)**:
     * Eksekusi berantai secara sekuensial dengan mengalirkan string data output (`sys.stdout` yang dialihkan ke `io.StringIO`) dari perintah kiri menjadi input standar (`sys.stdin` dialihkan ke `io.StringIO`) perintah kanan berikutnya.

4. **Perbaikan Kompatibilitas & Ketahanan Sistem Operasi (macOS & UNIX)**:
   * **Scoping Raw Mode**: Membatasi pengaktifan raw mode hanya saat pembacaan masukan di `read_line_interactive()`. Begitu Enter ditekan, kursor dinonaktifkan dari raw mode sebelum baris baru dicetak. Ini memecahkan masalah layout berantakan (*stair-stepping*) pada built-in commands (seperti `help`, `pwd`, `dir`) dan prompt berikutnya di macOS.
   * **Buffering Stdin Bypass**: Mengubah pembacaan masukan pada `get_char` di macOS/UNIX dari `sys.stdin.read(1)` menjadi `os.read(0, 1)` tingkat rendah. Hal ini memecahkan isu buffering Python yang memotong escape sequence tombol arah panah (Atas/Bawah untuk riwayat, Kiri/Kanan untuk pergerakan kursor).
   * **Restorasi Instan & Otomatis**:
     * Mengubah transisi kontrol terminal menggunakan parameter `termios.TCSANOW` agar restorasi mode terminal berjalan seketika.
     * Mengintegrasikan `atexit.register(disable_raw_mode)` agar status terminal pengguna dijamin kembali normal (cooked mode) jika program shell keluar secara tidak terduga atau crash.
     * Menambahkan pemulihan Cooked Mode paksa di fungsi `setup_terminal()` saat startup untuk menetralisir terminal jika pengguna membuka shell setelah crash pada sesi sebelumnya.

---

## Bab 2: Struktur Berkas & Modul yang Diperbarui

Struktur direktori proyek saat ini setelah penyelesaian Tahap 5 adalah sebagai berikut:

```text
Cyanix-CLI-Shell/
├── config.py
├── shell.py
├── reports/
│   ├── REPORTS_1.md
│   ├── REPORTS_2.md
│   ├── REPORTS_3.md
│   ├── REPORTS_4.md
│   └── REPORTS_5.md
└── utils/
    ├── __init__.py
    ├── builtins.py
    └── parser.py
```

Peran berkas yang mengalami modifikasi besar pada tahap ini meliputi:
- **`config.py`**: Memperbarui ANSI escape codes ke format 256-color agar kompatibel penuh dengan macOS Terminal.app & Windows PowerShell. Menambahkan pemulihan cooked mode paksa pada `setup_terminal()` di UNIX.
- **`shell.py`**: Mengubah alur raw mode agar tersangkut hanya di dalam pemanggilan input, memprogram pembacaan input langsung via `os.read(0, 1)`, membenahi deteksi tombol arah panah, dan mendaftarkan pembersihan `atexit`.
- **`utils/builtins.py`**: Menambahkan perintah murni `grep`, helper parsing redirection (`<`, `>`), pemisah pipeline (`|`), dan merombak `execute_command` dengan arsitektur POSIX fork-exec-pipe tingkat rendah serta fallback berantai di Windows.
- **`utils/parser.py`**: Menambahkan fungsi pra-pemrosesan `preprocess_line()` guna menyisipkan spasi di sekitar operator `|`, >, dan < agar ter-tokenisasi dengan benar oleh parser.

---

## Bab 3: Kesimpulan

Dengan diselesaikannya Tahap 5, **Cyanix-CLI-Shell (CyanSh)** kini telah bertransformasi menjadi shell CLI yang canggih, robust, dan andal secara lintas platform. Shell tidak hanya mampu mengelola alur proses internal dan eksternal, melainkan juga memiliki kemampuan penuh dalam memanipulasi aliran data I/O (Redirection), merangkai pipa komputasi antar-proses (Piping), serta menyediakan perintah pencarian teks terintegrasi (`grep`) dengan performa stabil dan layout terminal yang rapi baik di Windows maupun macOS.
