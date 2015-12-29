from twisted.internet import reactor, defer
from twisted.names import client, dns, error, server

class DynamicResolver(object):
    _myprefix = "8.b.d.0.1.0.0.2.ip6.arpa"
    _mysuffix = ".example.net"
    def _ResponseRequired(self, query):
        if query.type == dns.PTR:
	    if query.name.name.endswith(self._myprefix):
		return True
        return False

    def _doDynamicResponse(self, query):
        myip = b'%s' % (query.name.name[:-9][::-1].replace(".",""))
	myptr = "-".join([myip[:4], myip[4:8], myip[8:12], myip[12:16], myip[16:20], myip[20:24], myip[24:28], myip[28:]])+self._mysuffix
	_payload = dns.Record_PTR(name=myptr)
        answer = dns.RRHeader(
            name=query.name.name,
	    type=_payload.TYPE,
	    ttl=3600,
	    auth=True,
	    payload=_payload)
        answers = [answer]
        authority = []
        additional = []
        return answers, authority, additional

    def query(self, query, timeout=None):
        if self._ResponseRequired(query):
            return defer.succeed(self._doDynamicResponse(query))
        else:
            return defer.fail(error.DomainError())

def main():
    factory = server.DNSServerFactory(
        clients=[DynamicResolver()]
    )

    protocol = dns.DNSDatagramProtocol(controller=factory)

    reactor.listenUDP(10053, protocol)
    reactor.listenTCP(10053, factory)

    reactor.run()

if __name__ == '__main__':
    raise SystemExit(main())
