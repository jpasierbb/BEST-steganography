from dnslib.server import DNSServer, BaseResolver
from dnslib import DNSRecord, RR, QTYPE, A

class StegoTXIDResolver(BaseResolver):
    def resolve(self, request, handler):
        txid = request.header.id
        qname = request.q.qname
        print(f"Received TXID: {txid}")
        
        reply = request.reply()
        reply.add_answer(RR(qname, QTYPE.A, ttl=60, rdata=A("192.0.2.1")))
        return reply

if __name__ == "__main__":
    resolver = StegoTXIDResolver()
    server = DNSServer(resolver, port=5353, address="127.0.0.1", tcp=False)
    server.start()
