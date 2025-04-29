import socket
import random
import time
from IO_ops import *
from dnslib import DNSRecord, DNSHeader, DNSQuestion, QTYPE


SPECIAL_CHAR = 0x0000

domains = ['teams.rnicrosoft.pl', 'outlook.rnicrosoft.pl', 'onedrive.rnicrosoft.pl']

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

    num_parts = random.randint(300, 350)  # dzielenie antygony na części 
    part_length = len(binary_data) // num_parts
    parts = []
    for i in range(num_parts):
        start = i * part_length
        if i == num_parts - 1:
            end = len(binary_data)
        else:
            end = (i + 1) * part_length
        parts.append(binary_data[start:end])


    start_end_website = random.choice(domains)
    # Start przesylania ukrytej wiadomosci
    client.sendto(dns_query(SPECIAL_CHAR, start_end_website).pack(), ('127.0.0.1', 5454))
    print(f"Sent START TXID: {SPECIAL_CHAR}")

    try:
        response, _ = client.recvfrom(512)
        print("Response received")
    except socket.timeout:
        print("No response received (timeout)")

    # Ukryte dane
    for part in parts:
        # Wysłanie znaku specjalnego START
        start_end_website = random.choice(domains)
        client.sendto(dns_query(SPECIAL_CHAR, start_end_website).pack(), ('127.0.0.1', 5454))
        print(f"Sent START TXID: {SPECIAL_CHAR}")

        try:
            response, _ = client.recvfrom(512)
        except socket.timeout:
            pass

        for i in range(0, len(part), 16):
            selected_website = random.choice(domains)
            chunk = part[i:i+16]
            if len(chunk) < 16:
                chunk = chunk.ljust(16, '0')  # Dopelnij zerami do 16 bitów
            
            chunk = mix_two_chars_bits(chunk)
            txid = int(chunk, 2)

            client.sendto(dns_query(txid, selected_website).pack(), ('127.0.0.1', 5454))
            print(f"Sent TXID: {txid} (chunk: {chunk})")

            try:
                response, _ = client.recvfrom(512)
            except socket.timeout:
                pass

        # Wysłanie znaku specjalnego STOP
        client.sendto(dns_query(SPECIAL_CHAR, start_end_website).pack(), ('127.0.0.1', 5454))
        print(f"Sent STOP TXID: {SPECIAL_CHAR}")

        try:
            response, _ = client.recvfrom(512)
        except socket.timeout:
            pass

        # Po każdej części wysyłamy fake messages
        num_fake_messages = random.randint(40, 60)
        send_fake_message(client, num_fake_messages, start_end_website)

def send_fake_message(client, num_fake_messages, start_end_website):
    for _ in range(num_fake_messages):
        # FAKE dane wygenerowane jak prawdziwe
        fake_bits = ''.join(random.choice('01') for _ in range(16))
        mixed_bits = mix_two_chars_bits(fake_bits)
        fake_txid = int(mixed_bits, 2)

        fake_website = random.choice(domains)
        print(f"Sending FAKE TXID: {fake_txid} (chunk: {mixed_bits})")
        client.sendto(dns_query(fake_txid, fake_website).pack(), ('127.0.0.1', 5454))




if __name__ == "__main__":
    filepath = "data/Sofokles-Antygona.txt"
    send_dns_query(filepath)
