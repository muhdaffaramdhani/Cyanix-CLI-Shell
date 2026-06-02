def parse_line(line: str) -> list[str]:
    """
    Memecah string input dari pengguna menjadi list token berdasarkan karakter spasi.
    Melakukan validasi terhadap batas panjang input (1024) dan jumlah argumen (64).
    """
    # 1. Validasi Panjang Input (Max 1024 Karakter)
    if len(line) > 1024:
        raise ValueError("cynix: error: input too long (max 1024 characters)")

    # 2. Tokenisasi menggunakan str.split() (Menangani spasi berlebih secara otomatis)
    tokens = line.split()

    # 3. Validasi Jumlah Argumen (Max 64 Token)
    if len(tokens) > 64:
        raise ValueError("cynix: error: too many arguments (max 64)")

    return tokens
