# Wczytywanie danych
def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='CP1250') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' does not exist")
    except Exception as e:
        print(f"Error: {e}")
    return None

# Zamiana znaku na binarny odpowiednik
def char_to_binary(char):
    return format(ord(char), '08b')

# Stworzenie listy
def text_to_binary_list(text):
    return [(char, char_to_binary(char)) for char in text]


if __name__ == "__main__":
    filepath = "data/Sofokles-Antygona.txt"
    text = read_file(filepath)
    if text is not None:
        binary_list = text_to_binary_list(text)
        print(binary_list)
        # for char, binary in binary_list:
        #     print(f"Znak: '{char}' -> {binary}")
