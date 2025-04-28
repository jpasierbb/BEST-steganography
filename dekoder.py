import pyshark
import sys
import os

SPECIAL_CHAR = 0x0000

def analyze_pcap(filepath):
    if not os.path.exists(filepath):
        print(f"[!] File {filepath} does not exist.")
        return

    capture = pyshark.FileCapture(filepath, display_filter='dns')
    print(f"[*] Analyzing pcap file: {filepath}")

    receiving = False
    chunks = []

    for packet in capture:
        try:
            if hasattr(packet, 'dns') and hasattr(packet.dns, 'id'):
                txid = int(packet.dns.id, 16)
                print(f"[*] Found TXID: {txid}")
                
                if txid == SPECIAL_CHAR and not receiving:
                    print("[*] Start hidden transmission detected.")
                    receiving = True
                    chunks = []
                elif txid == SPECIAL_CHAR and receiving:
                    print("[*] End hidden transmission detected.")
                    receiving = False
                    reconstruct_message(chunks)
                elif receiving:
                    # Przemieszaj odebrane bity
                    mixed_chunk = format(txid, '016b')
                    demixed_chunk = demix_two_chars_bits(mixed_chunk)
                    chunks.append(demixed_chunk)
        except AttributeError:
            continue

    capture.close()

def demix_two_chars_bits(mixed):
    # Odwraca mieszanie:
    bits1 = mixed[:4] + mixed[8:10] + mixed[12:14]
    bits2 = mixed[4:8] + mixed[10:12] + mixed[14:]
    return bits1 + bits2

def reconstruct_message(chunks):
    full_bits = ''.join(chunks)

    # Jeśli niepełne bajty - przytnij
    if len(full_bits) % 8 != 0:
        full_bits = full_bits[:len(full_bits) - (len(full_bits) % 8)]

    byte_array = [int(full_bits[i:i+8], 2) for i in range(0, len(full_bits), 8)]
    message_bytes = bytes(byte_array)

    try:
        message = message_bytes.decode('utf-8')
        print("[*] Hidden message reconstructed:")
        print(message)

        # Zapisz do pliku
        os.makedirs('data', exist_ok=True)
        with open('data/decoded_message.txt', 'w', encoding='utf-8') as f:
            f.write(message)
        print("[*] Message saved to data/decoded_message.txt")

    except Exception as e:
        print(f"[!] Error decoding message: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <pcap_file>")
        sys.exit(1)

    pcap_filename = sys.argv[1]
    full_path = os.path.join('pcap', pcap_filename)

    analyze_pcap(full_path)
