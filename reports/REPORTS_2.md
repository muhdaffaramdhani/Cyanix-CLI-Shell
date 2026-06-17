# Laporan Pengembangan Tahap 2 — Cyanix-CLI-Shell (CyanSh)

Dokumen ini menjelaskan implementasi fitur, teknik penanganan string, dan struktur sistem yang diselesaikan pada **Tahap 2** pengembangan prototipe **Cyanix-CLI-Shell (CyanSh)**.

---

## Bab 1: Apa yang Sudah Diimplementasikan

Pada Tahap 2, pengembangan difokuskan untuk memproses string mentah masukan pengguna menjadi struktur data terpisah (token) yang dapat dipahami dan divalidasi oleh shell:

1. **Pemecahan Perintah (*Command Tokenization*)**:
   Mengubah string input tunggal yang diketik pengguna menjadi daftar (*list/array*) token argumen terpisah berdasarkan karakter spasi sebagai pemisah (*delimiter*).

2. **Integrasi Pustaka `shlex` untuk Penanganan Tanda Kutip (*Quotes*)**:
   Menggunakan modul `shlex.split()` daripada fungsi `string.split()` standar. Hal ini dilakukan agar argumen yang berada di dalam tanda kutip ganda (`"..."`) atau tanda kutip tunggal (`'...'`) tetap dipertahankan sebagai satu kesatuan argumen (tidak terpecah meskipun mengandung spasi), serta menangani karakter backslash (`\`) sebagai karakter escape dengan benar.

3. **Validasi Panjang Batas Input Maksimal 1024 Karakter**:
   Menolak memproses baris perintah apabila jumlah karakter yang diketik oleh pengguna melebihi 1024 karakter untuk menjaga keandalan memori.

4. **Validasi Jumlah Argumen Maksimal 64 Token**:
   Membatasi jumlah token yang diuraikan maksimal 64 argumen (termasuk perintah utama) untuk mencegah beban memori berlebih dan mencegah eksploitasi parameter.

---

## Bab 2: Struktur Berkas & Modul

Pada Tahap 2, proyek mulai dibagi secara modular untuk memisahkan logika antarmuka dan penguraian perintah:

```plaintext
Cyanix-CLI-Shell/
├── shell.py
└── utils/
    ├── __init__.py
    └── parser.py
```

- **`shell.py`**: Memanggil modul pengurai (`parse_line`) dari sub-folder utilitas dan mencetak hasil parsing token untuk kebutuhan penelusuran (*debugging*).
- **`utils/parser.py`**: Modul utilitas baru yang bertanggung jawab penuh terhadap analisis sintaksis string input, validasi panjang karakter, penguraian token menggunakan `shlex`, dan validasi jumlah argumen.
- **`utils/__init__.py`**: Membuat fungsi `parse_line` dapat diekspor ke modul luar dengan rapi.

---

## Bab 3: Detail Section Penugasan

### A. Capaian
- Pengguna dapat memasukkan parameter perintah yang kompleks secara berurutan.
- Parameter yang mengandung karakter spasi (misalnya nama direktori `folder baru`) dapat dibaca secara utuh dengan membungkusnya dalam tanda kutip.
- Sistem mampu menolak input yang melebihi batas batas aman (panjang masukan > 1024 karakter atau jumlah argumen > 64) dengan melemparkan pengecualian pesan error terstruktur.

### B. Progress dan Problem
- **Problem**: Penggunaan pemisahan string berbasis spasi mentah (`line.split()`) memecah parameter yang berharga seperti nama file dengan spasi (misal: `cp "laporan lama.txt" "laporan baru.txt"` akan terpecah menjadi 5 argumen, bukan 3).
- **Solusi**: Mengganti parser mentah menggunakan `shlex.split()`. Fungsi ini secara otomatis mem-parsing tanda kutip, mempertahankan spasi di dalam kutip, dan menghapus tanda kutip luar dari argumen saat disimpan di dalam list.

### C. Testing Skenario

| No | Skenario Uji Coba | Langkah Uji | Hasil yang Diharapkan | Status |
|----|---|---|---|---|
| 1 | Penanganan Argumen dengan Spasi | Memasukkan perintah `mkdir "folder baru"` | Terurai menjadi 2 argumen: `args[0] = "mkdir"`, `args[1] = "folder baru"` | Lolos |
| 2 | Proteksi Panjang Karakter | Menginput string acak sepanjang 1025 karakter atau lebih | Sistem membatalkan eksekusi perintah dan mencetak error: `cynix: error: input terlalu panjang (maksimal 1024 karakter)` | Lolos |
| 3 | Proteksi Batas Argumen | Memasukkan input perintah dengan 65 argumen terpisah spasi | Sistem membatalkan eksekusi perintah dan mencetak error: `cynix: error: terlalu banyak argumen (maksimal 64)` | Lolos |

### D. Contoh Penggunaan

Simulasi visual keluaran pada terminal saat penelusuran (*debug mode*) diaktifkan pada Tahap 2:

```plaintext
Muh Daffa@Lenovo-L380-Yoga CyanixOS ~
$ cp "laporan uas.txt" d:/backup/
[DEBUG] Tokenized arguments:
  args[0] = "cp"
  args[1] = "laporan uas.txt"
  args[2] = "d:/backup/"

Muh Daffa@Lenovo-L380-Yoga CyanixOS ~
$ 
```

### E. Tahap Lanjutan
Pada tahap berikutnya (Tahap 3), fokus pengembangan adalah mengimplementasikan fungsionalitas perintah internal bawaan (*built-in*) dasar seperti perpindahan direktori (`cd`), cetak lokasi direktori aktif (`pwd`), kustomisasi penjelajah berkas kustom (`dir`), dan pembagian struktur program yang lebih modular.