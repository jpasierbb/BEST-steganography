from dnslib.server import DNSServer, BaseResolver
from dnslib import DNSRecord, RR, QTYPE, A


SPECIAL_CHAR = 0x0000


class StegoTXIDResolver(BaseResolver):
    def __init__(self):
        self.receiving = False
        self.chunks = []

    def resolve(self, request, handler):
        txid = request.header.id
        qname = request.q.qname
        print(f"Received TXID: {txid}")
        
        reply = request.reply()
        reply.add_answer(RR(qname, QTYPE.A, ttl=1, rdata=A("192.0.2.1")))

        if txid == SPECIAL_CHAR and not self.receiving:
            print("[*] Start receiving hidden message...")
            self.receiving = True
            self.chunks = []

        elif txid == SPECIAL_CHAR and self.receiving:
            print("[*] End of message.")
            self.receiving = False
            self.process_message()

        elif self.receiving:
            adjusted_txid = txid #- (1500 if txid % 2 == 0 else 850)
            chunk = format(adjusted_txid, '016b')
            mixed_chunk = self.demix_two_chars_bits(chunk)
            self.chunks.append(mixed_chunk)

        return reply

    def demix_two_chars_bits(self, mixed):
        bits1 = mixed[:4] + mixed[8:10] + mixed[12:14]
        bits2 = mixed[4:8] + mixed[10:12] + mixed[14:]
        return bits1 + bits2
    
    def process_message(self):
        full_bits = ''.join(self.chunks)
        message = self.binary_to_text(full_bits)
        print("[*] Hidden message reconstructed:")
        print(message)
        with open("data/hidden_message.txt", "w", encoding="CP1250") as f:
            f.write(message)
        print("[*] Message saved to hidden_message.txt")
    
    # TODO cos tu nie dziala z kodowaniem, ale niby przesyal wszystko ok
    def binary_to_text(self, full_bits):
        # Sprawdź, czy ostatni bajt to same zera
        if len(full_bits) % 8 == 0:  # Upewnij się, że mamy pełne bajty
            last_byte = full_bits[-8:]
            if last_byte == "00000000":  # Jeśli ostatni bajt to same zera, usuń go
                full_bits = full_bits[:-8]
        
        # Podziel na bajty (8 bitów) i konwertuj
        byte_array = [full_bits[i:i+8] for i in range(0, len(full_bits), 8)]
        
        # Przekształć na znaki
        decoded_message = ''.join(chr(int(byte, 2)) for byte in byte_array)
        
        try:
            # Zdekoduj z użyciem CP1250
            return decoded_message.encode('cp1250').decode('cp1250')
        except UnicodeDecodeError as e:
            print(f"Error decoding message: {e}")
            return None


if __name__ == "__main__":
    resolver = StegoTXIDResolver()
    server = DNSServer(resolver, port=5353, address="127.0.0.1", tcp=False)
    server.start()
