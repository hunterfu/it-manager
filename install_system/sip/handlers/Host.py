from piston.handler import BaseHandler
from sip.models import Host, Nic

class HostHandler(BaseHandler):
    allow_methods   = ('GET','POST')
    model           = Host

    base    = Host.objects
    def read(self, request, sn):
        base = self.base
        if sn:
            return base.get(sn=sn)
        else:
            return base.all()

    def create(self, request):
        data = request.data
        sn=data['sn']
        hostname=data['hostname']
        oob_url=data.get('oob_url', None)
        print sn, hostname
        try:
            h = Host.objects.get(sn=sn)
            h.hostname = hostname
            h.oob_url = oob_url
        except Host.DoesNotExist:
            h = self.model(
                sn=sn,
                hostname=hostname,
                oob_url=oob_url,
                )
        h.save()
        nic1 = Nic(eth_no=0, switch_port=data.get('sp', ""), ip=data.get('ip',""), host=h)
        nic2 = Nic(eth_no=1, switch_port=data.get('sp2', ""), ip=data.get('ip2',""), host=h)
        nic1.save()
        nic2.save()
        
        return True

