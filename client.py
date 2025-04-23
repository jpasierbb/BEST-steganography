import socket
import random
from dnslib import DNSRecord, DNSHeader, DNSQuestion, QTYPE

def encode_data(data):
    return ''.join(format(ord(i), '08b') for i in data)

def send_dns_query(data):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(2)
    
    binary_data = encode_data(data)
    
    for i in range(0, len(binary_data), 16):
        chunk = binary_data[i:i+16]
        if len(chunk) < 16:
            chunk = chunk.ljust(16, '0')
        txid = int(chunk, 2)
        
        # Zapytanie DNS
        query = DNSRecord(
            DNSHeader(id=txid),
            q=DNSQuestion("example.com", QTYPE.A)
        )
        
        client.sendto(query.pack(), ('127.0.0.1', 5353))
        print(f"Sent TXID: {txid}")

    try:
        response, _ = client.recvfrom(512)
        print("Response received")
    except socket.timeout:
        print("No response received (timeout)")

if __name__ == "__main__":
    send_dns_query("secret")
