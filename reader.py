from scapy.all import *
from scapy.layers.dns import DNS
import os

while True:
    path = input("Wklej ścieżkę pliku .pcap: ")

    if os.path.isfile(path):
        try:
            dns_packets = rdpcap(path)
            print("Plik został wczytany.")
            break
        except Exception as e:
            print(f"Wystąpił błąd {e}\n Spróbuj ponownie.\n")
    else:
        print("Błąd: Ścieżka nieprawidłowa, spróbuj ponownie. \n")


zero_count = 0
for pkt in dns_packets:
    if pkt.haslayer(DNS):
        dns_layer = pkt[DNS]
        transaction_id = dns_layer.id
        if transaction_id == 0 and zero_count <= 4:
            zero_count += 1

if zero_count == 4:
    print("W tym pliku znajdują się zaszyfrowane dane")
else:
    print("Brak zaszyfrowanych danych")
