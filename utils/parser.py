import shlex

def parse_line(line: str) -> list[str]:
    # 1. Validasi Panjang Input (Max 1024 Karakter)
    if len(line) > 1024:
        raise ValueError("cynix: error: input terlalu panjang (maksimal 1024 karakter)")

    # 2. Tokenisasi
    try:
        # shlex.split handles quotes and backslashes correctly (removing them for args)
        tokens = shlex.split(line)
    except ValueError as e:
        raise ValueError(f"cynix: error: {e}")

    # 3. Validasi Jumlah Argumen
    if len(tokens) > 64:
        raise ValueError("cynix: error: terlalu banyak argumen (maksimal 64)")

    return tokens