import random
import math

def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='cp1250') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' does not exist")
    except Exception as e:
        print(f"Error: {e}")
    return None

def write_file(filepath, data):
    try:
        with open(filepath, "w", encoding="cp1250", errors='replace') as f:
                f.write(data)
        print(f"Data saved to {filepath}")
    except OSError as e:
        print(f"Saving data to {filepath} error: {e}")

# Zamiana bajtu na binarny odpowiednik
def byte_to_binary(byte):
    return format(byte, '08b')

# Stworzenie listy bajtów
def text_to_binary_list(text):
    bytes_data = text.encode('utf-8')  # zamieniamy na bajty UTF-8
    return [(byte, byte_to_binary(byte)) for byte in bytes_data]

# Dzieli tekst na 7 paczek, z ktorych kazda jest mniejsza niz 10 kB
# Pisal GPT
def split_text_to_chunks(
    text: str,
    num_chunks: int = 7,
    max_chunk_size_bytes: int = 10240
) -> list[str]:
    data = text.encode('utf-8')
    total_bytes = len(data)
    if total_bytes > num_chunks * max_chunk_size_bytes:
        raise ValueError(
            f"Tekst ({total_bytes} bajtów) nie zmieści się w {num_chunks} paczkach po {max_chunk_size_bytes} bajtów"
        )

    # Generujemy wagi od num_chunks do 1, by uzyskać różne długości
    weights = list(range(num_chunks, 0, -1))
    sum_weights = sum(weights)

    # Obliczamy targety (bajty) dla każdej paczki
    targets = [
        min(math.ceil(total_bytes * w / sum_weights), max_chunk_size_bytes)
        for w in weights[:-1]
    ]
    used = sum(targets)
    targets.append(total_bytes - used)

    # Jeśli któryś przekracza limit, rozdziel równomiernie
    if any(t > max_chunk_size_bytes for t in targets):
        avg = math.ceil(total_bytes / num_chunks)
        targets = [min(avg, max_chunk_size_bytes) for _ in range(num_chunks)]

    # Budujemy fragmenty bez łamania bajtów UTF-8
    chunks: List[str] = []
    idx = 0
    text_len = len(text)
    for size in targets:
        if idx >= text_len:
            chunks.append("")
            continue
        chunk_bytes = 0
        chars: List[str] = []
        while idx < text_len:
            ch = text[idx]
            chb = ch.encode('utf-8')
            if chunk_bytes + len(chb) > size and chunk_bytes > 0:
                break
            chars.append(ch)
            chunk_bytes += len(chb)
            idx += 1
        chunks.append("".join(chars))
    return chunks



if __name__ == "__main__":
    filepath = "data/Sofokles-Antygona.txt"
    text = read_file(filepath)
    if text is not None:
        # binary_list = text_to_binary_list(text)
        # print(binary_list)
        packets = split_text_to_chunks(text)
        print(packets)
        for i, part in enumerate(packets, start=1):
            print(f"Fragment {i}: {len(part.encode('utf-8'))} bajtów, {len(part)} znaków")

