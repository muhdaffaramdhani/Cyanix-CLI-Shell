# Laporan Pengembangan Tahap 1 — Cyanix-CLI-Shell (CyanSh)

Dokumen ini menjelaskan implementasi fitur, mekanisme dasar, dan struktur sistem yang diselesaikan pada **Tahap 1** pengembangan prototipe **Cyanix-CLI-Shell (CyanSh)**.

---

## Bab 1: Apa yang Sudah Diimplementasikan

Pada Tahap 1, pengembangan difokuskan pada penyediaan fondasi utama dari sebuah Command Line Interface (CLI) menggunakan bahasa pemrograman Python:

1. **Struktur Utama REPL (Read-Evaluate-Print Loop) Berbasis Infinite Loop**:
   Membangun struktur perulangan tanpa henti (`while True`) untuk terus-menerus meminta input dari pengguna, mengevaluasi string input tersebut, mencetak respons (jika ada), dan mengulangi siklus tersebut secara berkelanjutan.

2. **Pengambilan Input String Interaktif**:
   Menggunakan fungsi input standar Python untuk menangkap baris teks yang diketik oleh pengguna setelah menekan tombol *Enter*.

3. **Prompt Kustom Dinamis**:
   Menampilkan petunjuk prompt kustom sebelum masukan diterima untuk membedakan antara sesi input shell dan respons sistem (misal: `user@device CyanixOS ~ $`).

4. **Perintah Kontrol Internal 'exit'**:
   Menerapkan instruksi kondisi sederhana untuk mendeteksi apabila string yang diketik pengguna adalah `exit`. Jika terdeteksi, program akan keluar secara bersih dari perulangan REPL dan mengakhiri eksekusi proses shell menggunakan kode status `0`.

---

## Bab 2: Struktur Berkas & Modul

Pada Tahap 1, struktur proyek sangat minimalis karena difokuskan sepenuhnya pada pembentukan loop utama program:

```text
Cyanix-CLI-Shell/
└── shell.py
```

- **`shell.py`**: Merupakan berkas utama program yang berisi kode inisialisasi terminal, deklarasi loop REPL (`while True`), pencetakan prompt kustom, pembacaan masukan teks standar dari pengguna, serta pemeriksaan logika terminasi perintah `exit`.

---

## Bab 3: Detail Section Penugasan

### A. Capaian
- Shell berhasil berjalan secara terus-menerus tanpa berhenti setelah menerima input biasa dari pengguna.
- Prompt kustom berhasil dicetak di sebelah kiri masukan teks secara konsisten.
- Input teks pengguna berhasil ditangkap secara lengkap.
- Perintah `exit` sukses meniadakan infinite loop dan memicu penutupan shell secara bersih tanpa memicu pengecualian (*exception error*).

### B. Progress dan Problem
- **Problem**: Penggunaan input standar pada Python terkadang langsung crash apabila pengguna menekan kombinasi tombol interupsi seperti Ctrl+C.
- **Solusi**: Menambahkan blok pengaman *exception handling* menggunakan `try...except KeyboardInterrupt` untuk menangkap sinyal interupsi keyboard agar program tidak langsung terhenti paksa (*force close*), melainkan sekadar mencetak baris kosong dan melanjutkan loop REPL.

### C. Testing Skenario

| No | Skenario Uji Coba | Langkah Uji | Hasil yang Diharapkan | Status |
|----|---|---|---|---|
| 1 | Menerima Masukan Kosong | Pengguna menekan tombol Enter tanpa mengetik teks apa pun | Shell tidak melakukan tindakan apa pun, tidak crash, dan menampilkan kembali prompt kustom pada baris berikutnya | Lolos |
| 2 | Mengetik Teks Acak (Non-perintah) | Mengetik teks bebas (contoh: `hallo dunia`) | Shell membaca input tersebut dan kembali ke loop pembacaan prompt tanpa crash (tidak memproses apa pun pada tahap ini) | Lolos |
| 3 | Pengakhiran Sesi Shell | Mengetik perintah `exit` lalu menekan Enter | Shell segera keluar dari program dan kontrol terminal dikembalikan ke sistem operasi hos | Lolos |

### D. Contoh Penggunaan

Simulasi visual keluaran pada terminal saat pengoperasian Tahap 1:

```text
Muh Daffa@Lenovo-L380-Yoga CyanixOS ~
$ 
Muh Daffa@Lenovo-L380-Yoga CyanixOS ~
$ hallo dunia
Muh Daffa@Lenovo-L380-Yoga CyanixOS ~
$ 
Muh Daffa@Lenovo-L380-Yoga CyanixOS ~
$ exit

d:\04_Dev>
```

### E. Tahap Lanjutan
Pada tahap berikutnya (Tahap 2), fokus pengembangan adalah memisahkan string masukan pengguna menjadi instruksi perintah utama dan argumen-argumennya (*Command Tokenization*), serta menerapkan validasi panjang masukan.
