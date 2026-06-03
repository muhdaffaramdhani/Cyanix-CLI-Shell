def parse_line(line: str) -> list[str]:
    # 1. Validasi Panjang Input (Max 1024 Karakter)
    if len(line) > 1024:
        raise ValueError("cynix: error: input too long (max 1024 characters)")

    # 2. Tokenisasi
    tokens = line.split()

    # 3. Validasi Jumlah Argumen
    if len(tokens) > 64:
        raise ValueError("cynix: error: too many arguments (max 64)")

    return tokens