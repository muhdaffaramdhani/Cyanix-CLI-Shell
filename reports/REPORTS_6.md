# Laporan Pengembangan Tahap 6 — Cyanix-CLI-Shell (CyanSh)

Dokumen ini menjelaskan hasil **pengujian beban dan penanganan eror (error handling)** yang dilakukan pada **Tahap 6** pengembangan prototipe **Cyanix-CLI-Shell (CyanSh)**. Fokus tahap ini adalah memastikan CLI tidak crash (force close) ketika menerima input yang tidak valid atau tidak terduga dari pengguna.

---

## Bab 1: Skenario Pengujian & Analisis Kode

### 1.1 Skenario 1 — Pengguna Menekan Enter Tanpa Mengetik Apa Pun

**Tujuan:** Memastikan shell tidak crash atau keluar saat pengguna menekan Enter pada prompt kosong.

**Mekanisme Penanganan:**

Perlindungan terhadap input kosong diimplementasikan di dua lapisan pertahanan:

* **Lapisan 1 — REPL Loop (`shell.py`, baris 671–674):**
  Setelah fungsi `read_line_interactive()` mengembalikan string input, hasilnya langsung di-`strip()` untuk membersihkan spasi. Jika hasilnya adalah string kosong (`""`), maka blok `if not raw_input: continue` akan langsung melewati iterasi dan kembali menampilkan prompt berikutnya **tanpa memproses apa pun**.

  ```python
  raw_input = read_line_interactive(prompt_prefix, history).strip()

  if not raw_input:
      continue
  ```

* **Lapisan 2 — Validasi Token (`shell.py`, baris 682–683):**
  Bahkan jika `raw_input` lolos pemeriksaan pertama (misalnya berisi hanya spasi-spasi yang lolos `strip()`), fungsi `parse_line()` akan mengembalikan list kosong `[]`. Pemeriksaan kedua `if not args: continue` akan menangkap kondisi ini.

  ```python
  if not args:
      continue
  ```

**Hasil Pengujian:**

| Input Pengguna | Perilaku Shell | Status |
|---|---|---|
| *(tekan Enter langsung)* | Shell mencetak prompt baru tanpa error | ✅ LULUS |
| *(spasi + Enter)* | Shell mencetak prompt baru tanpa error | ✅ LULUS |
| *(tab + Enter)* | Shell mencetak prompt baru tanpa error | ✅ LULUS |

---

### 1.2 Skenario 2 — Pengguna Memasukkan Perintah yang Tidak Dikenal

**Tujuan:** Menampilkan pesan "Command not found" yang informatif tanpa crash.

**Mekanisme Penanganan:**

Shell memiliki mekanisme routing perintah bertingkat di dalam fungsi `execute_single_command()` (`utils/builtins.py`, baris 469–572):

1. **Pencocokan Built-in:** Perintah dicek terlebih dahulu terhadap set `BUILTINS` yang berisi semua perintah bawaan (`cd`, `pwd`, `help`, `dir`, `mkdir`, `touch`, `cat`, `cp`, `mv`, `rm`, `grep`, `debug`, `cls`, `clear`, `exit`) beserta shortcut drive Windows (misalnya `c:`, `d:`).

2. **Fallback Eksekusi Eksternal:** Jika perintah tidak ditemukan di daftar built-in, shell mencoba mengeksekusinya sebagai program eksternal:
   * **POSIX/UNIX**: Menggunakan `os.fork()` + `os.execvp()`. Jika binary tidak ditemukan, exception `FileNotFoundError` ditangkap dan mencetak pesan:
     ```
     cynix: perintah tidak ditemukan: [nama_perintah]
     ```
     Child process keluar dengan kode `127` via `os._exit(127)`, sementara parent process tetap menunggu dengan `os.waitpid()` dan kembali ke REPL secara normal.

   * **Windows**: Menggunakan `subprocess.run()`. Jika gagal (`FileNotFoundError`), shell mencoba lagi dengan `shell=True`. Jika tetap tidak ditemukan, mencetak pesan:
     ```
     '[nama_perintah]' tidak dikenali sebagai perintah internal atau eksternal, program yang dapat dijalankan, atau file batch.
     ```

3. **Penanganan Exception Tambahan:** Seluruh blok eksekusi dibungkus oleh `try-except` yang menangkap `KeyboardInterrupt` (agar Ctrl+C tidak mematikan shell) dan `Exception` generik sebagai jaring pengaman terakhir.

**Hasil Pengujian:**

| Input Pengguna | Output Shell | Status |
|---|---|---|
| `xyzabc` | `'xyzabc' tidak dikenali sebagai perintah internal atau eksternal...` | ✅ LULUS |
| `perintahpalsu` | `'perintahpalsu' tidak dikenali sebagai perintah internal atau eksternal...` | ✅ LULUS |
| `123` | `'123' tidak dikenali sebagai perintah internal atau eksternal...` | ✅ LULUS |
| `!@#$%` | Ditangani parser / dicetak error tanpa crash | ✅ LULUS |

---

### 1.3 Skenario 3 — Pengguna Memasukkan Terlalu Banyak Argumen atau Spasi Berlebih

**Tujuan:** Memastikan shell tidak crash saat menerima input dengan spasi berlebih atau argumen yang sangat banyak.

**Mekanisme Penanganan:**

Perlindungan diimplementasikan di **tiga lapisan** berbeda:

* **Lapisan 1 — Proteksi Real-time di Input Loop (`shell.py`, baris 620–622):**
  Pada saat pengguna mengetik setiap karakter, fungsi `check_arg_limit()` dipanggil secara real-time **sebelum karakter dimasukkan ke buffer**. Fungsi ini mensimulasikan tokenisasi menggunakan `shlex.split()` dan menolak karakter baru jika jumlah token sudah mencapai batas **64 argumen**.

  ```python
  if len(buffer) < 1024 and check_arg_limit(buffer, c, pos):
      buffer.insert(pos, c)
      pos += 1
  ```

  Hal ini berarti pengguna **secara fisik tidak dapat mengetik lebih dari 64 argumen** di dalam prompt interaktif. Buffer juga dibatasi pada **1024 karakter** maksimum.

* **Lapisan 2 — Validasi Parser (`utils/parser.py`, baris 27–28 dan 41–42):**
  Sebagai garis pertahanan kedua (untuk input non-interaktif), `parse_line()` melakukan dua validasi:
  1. Panjang input maksimal 1024 karakter → Jika melebihi, melempar `ValueError` dengan pesan: `cynix: error: input terlalu panjang (maksimal 1024 karakter)`.
  2. Jumlah token maksimal 64 argumen → Jika melebihi, melempar `ValueError` dengan pesan: `cynix: error: terlalu banyak argumen (maksimal 64)`.

  ```python
  if len(line) > 1024:
      raise ValueError("cynix: error: input terlalu panjang (maksimal 1024 karakter)")
  # ...
  if len(tokens) > 64:
      raise ValueError("cynix: error: terlalu banyak argumen (maksimal 64)")
  ```

* **Lapisan 3 — Normalisasi Spasi oleh Tokenizer (`shlex.split`):**
  Spasi berlebih di antara argumen secara otomatis dinormalisasi oleh `shlex.split()` pada tahap tokenisasi. Spasi ganda, triple, atau lebih diabaikan dan tidak menghasilkan token kosong.

  ```
  Input:  "cd     ..     "   →   Token: ["cd", ".."]
  Input:  "   dir    -a  "   →   Token: ["dir", "-a"]
  ```

* **Penanganan Tanda Kutip Tidak Lengkap:**
  Jika pengguna memasukkan tanda kutip pembuka tanpa penutup (contoh: `cat "file`), `shlex.split()` akan melempar `ValueError`, yang ditangkap oleh blok `try-except` di `parse_line()` dan dicetak sebagai pesan error tanpa crash:
  ```
  cynix: error: No closing quotation
  ```

**Hasil Pengujian:**

| Input Pengguna | Perilaku Shell | Status |
|---|---|---|
| `cd      ..` (spasi berlebih) | Dinormalisasi menjadi `["cd", ".."]`, berhasil pindah direktori | ✅ LULUS |
| `    dir     -a    ` (spasi di awal, tengah, akhir) | Dinormalisasi menjadi `["dir", "-a"]`, menampilkan isi direktori | ✅ LULUS |
| Mengetik 65+ argumen secara interaktif | Input diblokir secara real-time, karakter baru ditolak | ✅ LULUS |
| String > 1024 karakter (non-interaktif) | Pesan error: `cynix: error: input terlalu panjang` | ✅ LULUS |
| `cat "file` (kutip tidak ditutup) | Pesan error: `cynix: error: No closing quotation` | ✅ LULUS |

---

## Bab 2: Ringkasan Arsitektur Pertahanan Eror

Berikut adalah diagram alur pertahanan error yang diterapkan pada CyanSh mulai dari input hingga eksekusi:

```
┌──────────────────────────────────────────────────────────┐
│                   PENGGUNA MENGETIK                       │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│  LAPISAN 1: Proteksi Real-time (shell.py)                │
│  • Buffer maks 1024 karakter                             │
│  • Argumen maks 64 token (check_arg_limit)               │
│  • Karakter baru DITOLAK jika melebihi batas             │
└──────────────┬───────────────────────────────────────────┘
               │ [Enter ditekan]
               ▼
┌──────────────────────────────────────────────────────────┐
│  LAPISAN 2: Validasi Input Kosong (shell.py)             │
│  • raw_input.strip() == "" → continue (prompt baru)      │
│  • args == [] → continue (prompt baru)                   │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│  LAPISAN 3: Tokenisasi & Validasi (parser.py)            │
│  • shlex.split() → normalisasi spasi                     │
│  • Validasi ulang panjang (1024) & argumen (64)          │
│  • ValueError pada kutip tidak lengkap                   │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│  LAPISAN 4: Routing & Eksekusi (builtins.py)             │
│  • Built-in → handler langsung + error handling          │
│  • Eksternal → fork/exec atau subprocess                 │
│  • Tidak ditemukan → pesan "command not found"           │
│  • Exception generik → pesan error, kembali ke REPL     │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│           KEMBALI KE PROMPT (REPL tetap berjalan)        │
└──────────────────────────────────────────────────────────┘
```

---

## Bab 3: Struktur Berkas & Modul yang Diperbarui

Tidak ada perubahan struktur berkas pada tahap ini. Laporan ini merupakan dokumentasi hasil pengujian terhadap kode yang sudah ada.

```text
Cyanix-CLI-Shell/
├── config.py
├── shell.py
├── reports/
│   ├── REPORTS_1.md
│   ├── REPORTS_2.md
│   ├── REPORTS_3.md
│   ├── REPORTS_4.md
│   ├── REPORTS_5.md
│   └── REPORTS_6.md      Laporan pengujian beban & penanganan eror
└── utils/
    ├── __init__.py
    ├── builtins.py
    └── parser.py
```

Berkas-berkas yang relevan dalam pengujian ini:
- **`shell.py`**: Mengandung REPL loop utama dengan validasi input kosong (baris 673–683) dan proteksi buffer/argumen real-time (baris 620–622).
- **`utils/parser.py`**: Mengandung validasi panjang input, tokenisasi `shlex.split()`, dan validasi jumlah argumen.
- **`utils/builtins.py`**: Mengandung routing perintah `execute_single_command()` dengan fallback ke pesan "command not found" untuk perintah tak dikenal, serta `try-except` menyeluruh di `execute_command()`.

---

## Bab 4: Kesimpulan

Hasil pengujian Tahap 6 menunjukkan bahwa **Cyanix-CLI-Shell (CyanSh)** telah memiliki ketahanan (*robustness*) yang solid terhadap berbagai bentuk kesalahan input pengguna. Shell mengimplementasikan **arsitektur pertahanan berlapis** (*defense-in-depth*) yang memastikan:

1. **Input kosong** ditangani secara diam (*silent*) — shell kembali ke prompt tanpa pesan error atau crash.
2. **Perintah tidak dikenal** menghasilkan pesan informatif yang jelas tanpa menghentikan program.
3. **Argumen berlebih dan spasi berlebih** ditangani secara proaktif melalui proteksi real-time dan normalisasi tokenizer.

Tidak ditemukan satupun skenario yang menyebabkan program *force close* atau melempar *unhandled exception* ke pengguna. Seluruh jalur error telah diinstrumentasi dengan pesan yang deskriptif dan REPL loop tetap berjalan stabil setelah setiap kesalahan.
