from piston.handler import BaseHandler
from piston.utils import rc, validate
from host.models import Server

class ServerHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    model = Server   
    base = Server.objects

    # read is called on GET requests, and should never modify data (idempotent.)
    def read(self, request, sn=None):
        """
        Returns a single server if `sn` is given,
        otherwise a subset.
        """
        base = self.base
        if sn:
            return base.get(sn=sn)
        else:
            return base.all()

    # create is called on POST, and creates new objects, and should return them (or rc.CREATED.)
    def create(self, request):
        """
        create server obj and save to db
        """
        data = request.data
        sn=data['sn']
        hostname = data.get('hostname',None)
        status = data.get('status', None)
        ip = data.get('ip', None)
        oob_ip = data.get('oob_ip', None)
        idc = data.get('idc', None)
        rack = data.get('rack', None)
        rack_no = data.get('rack_no', None)
        base =  self.base
        try:
            h = base.get(sn=sn)
            h.hostname = hostname
            h.status = status
            h.ip = ip
            h.oob_ip = oob_ip
            h.idc = idc
            h.rack = rack
            h.rack_no = rack_no
            h.save()
            return "UPDATED"

        except Server.DoesNotExist:
            h = self.model(
                sn=sn,
                hostname=hostname,
                ip=ip,
                oob_ip=oob_ip,
                idc=idc,
                rack = rack,
                rack_no = rack_no
                )
            h.save()

            return "CREATED"

