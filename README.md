# Cynix-CLI-Shell (CyanSh)

Cynix-CLI-Shell adalah implementasi **custom shell berbasis CLI** yang terinspirasi dari konsep arsitektur **Cyanix OS** — konsep sistem operasi berbasis microkernel yang dikembangkan oleh Kelompok 7. Shell ini adalah implementasi dari prinsip-prinsip desain yang telah dirancang dalam laporan konsep OS, seperti:

- **Security by Design** → setiap proses berjalan terisolasi, tidak boleh crash sembarangan
- **Modular Robustness** → komponen shell dipisah dengan jelas (built-in vs external vs advanced)
- **Least Privilege** → proses anak tidak mewarisi lebih dari yang dibutuhkan
- **IPC via Message Passing** → representasi dari mekanisme `fork()` + `pipe()` sebagai analogi IPC di Cyanix OS

Shell ini dinamakan **Cynix-CLI-Shell** sebagai referensi langsung ke *CyanSh (Cyan Shell)* yang disebutkan dalam dokumen laporan konsep Cyanix OS.

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

## Fitur yang Sudah Diimplementasikan

### 1. Tahap 0 — Splash Screen & Boot Banner
* **Target:** Menampilkan identitas visual dan karakteristik arsitektur sistem operasi Cyanix OS saat shell pertama kali dijalankan.
* **Visual Branding (ASCII Art):** Menampilkan logo utama `CYANIX OS` menggunakan representasi *box-drawing* karakter Unicode True Color dengan kode warna Cyan khas (`#13AFD7`).
* **Spesifikasi Informasi CLI:** Menyajikan tabel informasi terstruktur mengenai profil shell, versi prototipe (`v1.0.0`), dependensi lingkungan POSIX, serta daftar kontributor pengembang kelompok 7.
* **Konfigurasi Terminal Otomatis:** Mengimplementasikan fungsi `setup_terminal()` untuk memastikan terminal dapat merender karakter UTF-8 serta mendukung *ANSI Escape Codes* dengan baik di platform Windows maupun Unix-like (POSIX).
* **Alur Eksekusi Tunggal:** Fungsi pembersihan layar (`clear`) dan pencetakan splash banner diisolasi agar hanya dieksekusi satu kali di awal fungsi `main()` sebelum program memasuki interaksi perulangan utama (*REPL loop*).

### 2. Tahap 1 — Membangun REPL (Read-Evaluate-Print Loop)
* **Target:** CLI dapat menerima input dari pengguna secara terus-menerus.
* **Infinite Loop:** Membuat struktur utama program menggunakan perulangan tanpa henti (`while True`) sehingga shell tetap aktif setelah mengeksekusi perintah.
* **Prompt Kustom:** Menampilkan prompt interaktif dengan format `user@cynix:~$ ` (atau sesuai dengan username sistem aktif secara dinamis) setiap kali menunggu input baru.
* **Membaca Input:** Menggunakan fungsi bawaan `input()` untuk membaca string perintah dari pengguna per baris.
* **Kondisi Berhenti:** Program akan keluar secara bersih (clean exit) dan menghentikan perulangan hanya jika pengguna mengetik perintah `exit` atau mengirimkan sinyal EOF (`Ctrl+D`).

### 3. Tahap 2 — Parsing Perintah (Command Tokenization)
* **Target:** Memecah string input yang dimasukkan pengguna menjadi komponen-komponen terpisah (perintah dan argumen) agar dapat dieksekusi oleh sistem.
* **Tokenisasi Berbasis Spasi:** Menggunakan fungsi `line.split()` untuk memecah string berdasarkan karakter spasi (` `), yang secara otomatis menangani dan membersihkan spasi berlebih di antara argumen.
* **Validasi Batas Panjang Input:** Menerapkan pembatasan keamanan dengan panjang input maksimal 1024 karakter. Jika input melebihi batas, sistem akan memicu *error* (`cynix: error: input too long (max 1024 characters)`) tanpa membuat shell crash.
* **Validasi Batas Jumlah Argumen:** Membatasi jumlah token/argumen maksimal sebanyak 64 token dalam satu baris perintah. Jika dilanggar, shell akan menampilkan pesan kesalahan yang informatif (`cynix: error: too many arguments (max 64)`).
* **Keterkaitan Sistem Operasi:** Proses tokenisasi ini diisolasi di dalam modul `utils/parser.py` sebagai representasi dari langkah awal persiapan data sebelum dialokasikan ke dalam PCB (*Process Control Block*).

---

## Struktur Proyek

```text
Cyanix-CLI-Shell/
│
├── shell.py              # Entry Point: Main REPL Loop & Splash Screen
│
├── utils/
│   ├── __init__.py       # Module Exporter
│   └── parser.py         # Parsing & Tokenization (Tahap 2)
│
├── .gitignore            # File konfigurasi Git
└── README.md             # Dokumentasi proyek
```

---

## Cara Menjalankan

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

### 4. Rencana Pengembangan Selanjutnya (Tahap 3 - Tahap 6)

#### Tahap 3 — Implementasi Built-in Commands
* **Target:** Mengeksekusi perintah dasar secara langsung di dalam proses shell utama tanpa melakukan pembuatan proses baru (*tanpa fork*) untuk mengubah *state* dari shell itu sendiri.
* **Fitur Wajib:**
  * `cd` : Mengubah direktori aktif shell menggunakan *system call* `os.chdir()` (atau `chdir()` pada level OS).
  * `pwd`: Menampilkan path direktori aktif saat ini menggunakan fungsi `os.getcwd()` (atau `getcwd()` pada level OS).

#### Tahap 4 — Forking & Eksekusi Perintah Eksternal
* **Target:** Mampu menjalankan perintah bawaan sistem operasi (seperti `ls`, `mkdir`, `clear`, dll) dengan menduplikasi proses shell.
* **Mekanisme Proses:**
  * **Child Process:** Menggunakan *system call* `fork()` untuk membuat proses anak, kemudian memanggil keluarga fungsi `exec()` (seperti `execvp()`) untuk mengganti gambar memori proses anak dengan program eksternal yang dituju.
  * **Parent Process:** Menggunakan fungsi `wait()` atau `waitpid()` agar CLI utama menahan diri (menunggu) hingga proses anak selesai dieksekusi sebelum memunculkan prompt kustom baru ke pengguna.

#### Tahap 5 — Fitur Lanjutan (Piping & I/O Redirection) `[Bonus Target]`
* **Target:** Memanipulasi *file descriptor* pada level sistem operasi untuk mengarahkan aliran data (Input/Output).
* **Fitur Manipulasi:**
  * **I/O Redirection (`>` atau `<`):** Mengalihkan output standar atau input standar dari/ke file teks eksternal dengan memanfaatkan fungsi manajemen deskriptor seperti `dup2()`. *Contoh:* `ls > hasil.txt`.
  * **Piping (`|`):** Menghubungkan output standar dari proses pertama langsung menjadi input standar untuk proses kedua menggunakan *system call* `pipe()`. *Contoh:* `ls | grep .txt`.

#### Tahap 6 — Pengujian Beban & Penanganan Eror (Robustness)
* **Target:** Memastikan stabilitas CLI agar memiliki ketahanan tinggi (*anti-crash*) dan tidak mengalami *force close* saat menerima anomali input.
* **Skenario Penanganan:**
  * Menangani input kosong (pengguna hanya menekan tombol `Enter` tanpa karakter apa pun).
  * Menampilkan pesan kesalahan standar `cynix: command not found` secara aman jika perintah luar tidak dikenali oleh sistem.
  * Melakukan pembersihan otomatis terhadap spasi berlebih (*whitespace*) serta membatasi argumen sesuai batas aman yang ditentukan pada struktur parser.
