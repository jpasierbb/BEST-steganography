import socket
import random
from IO_ops import *
from dnslib import DNSRecord, DNSHeader, DNSQuestion, QTYPE


def mix_two_chars_bits(chunk):
    bits1 = chunk[0:7]
    bits2 = chunk[8:]
    mixed = bits1[:4] + bits2[:4] + bits1[4:] + bits2[4:]
    return mixed

def modify_txid_based_on_last_bits(chunk):
    last_two_bits = chunk[-2:]  # Ostatnie 2 bity
    last_two_int = int(last_two_bits, 2)
    
    if last_two_int % 2 == 0:
        return 1500
    else:
        return 850

def send_dns_query(filepath):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(2)
    
    text = read_file(filepath)
    if text is None:
        print(f"Error with reading data from a file {filepath}")
        return
    
    binary_list = text_to_binary_list(text)
    binary_data = ''.join(binary for _, binary in binary_list)
    
    for i in range(0, len(binary_data), 16):
        chunk = binary_data[i:i+16]
        if len(chunk) < 16:
            chunk = chunk.ljust(16, '0')  # Dopelnij zerami do 16 bitów
        
        chunk = mix_two_chars_bits(chunk)
        number_to_add = modify_txid_based_on_last_bits(chunk)
        txid = int(chunk, 2)  # Konwersją bitów na int
        
        # DNS query
        query = DNSRecord(
            DNSHeader(id=txid),
            q=DNSQuestion("teams.rnicrosoft.pl", QTYPE.A)
        )
        
        client.sendto(query.pack(), ('127.0.0.1', 5353))
        print(f"Sent TXID: {txid} (chunk: {chunk})")

    # Koniec przesylania ukrytej wiadomosci
    end_txid = 0x0000
    end_query = DNSRecord(
        DNSHeader(id=end_txid),
        q=DNSQuestion("teams.rnicrosoft.pl", QTYPE.A)
    )
    client.sendto(end_query.pack(), ('127.0.0.1', 5353))
    print(f"Sent END TXID: {end_txid} (chunk: 0000000000000000)")

    try:
        response, _ = client.recvfrom(512)
        print("Response received")
    except socket.timeout:
        print("No response received (timeout)")


if __name__ == "__main__":
    filepath = "data/Sofokles-Antygona.txt"
    send_dns_query(filepath)
