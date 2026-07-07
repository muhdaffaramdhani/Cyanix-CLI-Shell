import shlex

def preprocess_line(line: str) -> str:
    result = []
    in_quote = None
    i = 0
    while i < len(line):
        char = line[i]
        if char in ('"', "'"):
            if in_quote == char:
                in_quote = None
            elif in_quote is None:
                in_quote = char
            result.append(char)
        elif char in ('|', '>', '<') and in_quote is None:
            if i > 0 and line[i-1] == '\\':
                result.append(char)
            else:
                result.append(f" {char} ")
        else:
            result.append(char)
        i += 1
    return "".join(result)

def parse_line(line: str) -> list[str]:
    if len(line) > 1024:
        raise ValueError("cynix: error: input terlalu panjang (maksimal 1024 karakter)")

    preprocessed = preprocess_line(line)

    try:
        tokens = shlex.split(preprocessed)
    except ValueError as e:
        raise ValueError(f"cynix: error: {e}")

    if len(tokens) > 64:
        raise ValueError("cynix: error: terlalu banyak argumen (maksimal 64)")

    return tokens