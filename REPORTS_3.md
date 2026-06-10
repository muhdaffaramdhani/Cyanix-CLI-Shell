# Laporan Pengembangan Tahap 3 — Cyanix-CLI-Shell (CyanSh)

Dokumen ini menjelaskan implementasi fitur dan perubahan struktural yang telah diselesaikan pada **Tahap 3** pengembangan prototipe **Cyanix-CLI-Shell (CyanSh)**.

---

## 1. Apa yang Sudah Diimplementasikan

Berikut adalah poin-poin utama yang telah dirancang, ditulis, dan diuji pada tahap ini:

1. **Pembaruan Format Prompt Shell**:
   Format tampilan prompt interaktif kini diperbarui menjadi dua baris agar lebih bersih dan informatif:
   - **Baris 1**: Menampilkan identitas pengguna, nama perangkat, label OS, dan direktori aktif secara dinamis:
     `{username}@{device} CyanixOS {path}` (dengan skema warna visual ANSI untuk membedakan elemen).
   - **Baris 2**: Baris input khusus untuk mengetik perintah diawali dengan prompt indicator:
     `$`
   - **Contoh**:
     `Muh Daffa@Lenovo-L380-Yoga CyanixOS D:/04_Dev/Main/Sistem Operasi/UAS/Cyanix-CLI-Shell`
     `$`

2. **Pembuatan Folder Konfigurasi `config.py` Baru**:
   - Memisahkan visual branding, ASCII art logo Cyanix OS, dan data kontributor tim kelompok 7 dari folder utama.
   - Mengintegrasikan fungsi pembantu `enable_raw_mode()` dan `disable_raw_mode()` untuk mengontrol input mentah konsol secara terpusat.

3. **Pembuatan Folder `utils/builtins.py` Baru**:
   - Folder terpisah yang didedikasikan khusus untuk menampung fungsi perintah internal (builtins) shell.
   - Menyediakan handler eksekusi subproses (`execute_command`) yang menjembatani jalannya perintah bawaan maupun binary eksternal hos.

4. **Refaktorisasi Folder `shell.py`**:
   - Struktur kode pada folder `shell.py` didekorasi ulang dan disederhanakan (*compact*) agar lebih bersih dan fokus pada *REPL loop* utama, pembacaan keypress interaktif, dan penanganan kursor.
   - Mengimpor fungsi pembantu, warna, dan perintah internal secara langsung dari `config.py` dan `utils/builtins.py`.

5. **Implementasi Perintah Builtin (`cd`, `pwd`, `dir`, dll.)**:
   - **`cd [path]` & `cd ..`**: Berpindah direktori aktif.
   - **`pwd`**: Menampilkan path kerja saat ini.
   - **`dir`**: Menampilkan isi direktori secara alfabetis (A-Z folder terlebih dahulu baru file) dengan layout mirip PowerShell (tanpa kolom `Mode`).
   - **Windows Drive Change**: Shortcut untuk berpindah drive di Windows secara instan dengan mengetik `[drive_letter]:` (misal: `c:` atau `d:`).
   - **`cls` & `clear`**: Menghapus tampilan layar terminal.
   - **`help` & `exit`**: Panduan perintah dan keluar dari program shell secara bersih.
