from piston.handler import BaseHandler
from piston.utils import rc, validate
from host.models import Server
from pprint import pprint

class ServerHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    model = Server   
    base = Server.objects

    # read is called on GET requests, and should never modify data (idempotent.)
    def read(self, request):
        """
        Returns a single server if `sn` is given,
        otherwise a subset.
        """
        base = self.base
        model = self.model
        data = request.GET
        print request.GET
        all_field = model._meta.get_all_field_names()
        if len(data) >=1:
            parameters = {}
            for field_name ,value in data.items():
                if field_name in all_field:
                    parameters[field_name] =  value
                else:
                    try:
                        (field,oper) = field_name.split("__")
                        if field in all_field and oper in ['lte','gte','gt','lt']:
                            parameters[field_name] = value
                    except:
                        pass
            if len(parameters) != 0:
                return base.filter(**parameters)
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
        model = self.model
        all_field = model._meta.get_all_field_names()
        try:
            h = base.get(sn=sn)
            print h
            for k, v in data.items():
                if k in all_field:
                    setattr(h, k, v)
            h.save()
            return "UPDATED"

        except Server.DoesNotExist:
            h = self.model()
            for k, v in data.items():
                if k in all_field:
                    setattr(h,k,v)
            h.save()
            return "CREATED"

