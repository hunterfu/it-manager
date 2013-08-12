from piston.handler import BaseHandler
from piston.utils import rc, validate
from host.models import Server
from pprint import pprint

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
            try:
                return base.get(sn=sn)
            except:
                #return HttpResponse("None", content_type='text/plain')
                return "None"
        else:
            return base.all()

    # create is called on POST, and creates new objects, and should return them (or rc.CREATED.)
    def create(self, request):
        """
        create server obj and save to db
        """
        data = request.data
        sn=data.get('sn',None)
        base =  self.base
        # server serial must be supply
        if not sn:
            return "ERROR,NO SN FIELD"

        try:
            h = base.get(sn=sn)
            for k, v in data.items():
                if k in ['hostname','status','ip','oob_ip','idc','rack','rack_no','ks_temp']:
                    setattr(h, k, v)
            h.save()
            return "UPDATED"

        except Server.DoesNotExist:
            h = self.model()
            for k, v in data.items():
                if k in ['sn','hostname','status','ip','oob_ip','idc','rack','rack_no','ks_temp']:
                    setattr(h,k,v)
            h.save()
            return "CREATED"

