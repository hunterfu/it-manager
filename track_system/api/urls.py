from django.conf.urls.defaults import *
from piston.resource import Resource
from api.handlers import ServerHandler

server_handler = Resource(ServerHandler)

urlpatterns = patterns('',
   url(r'^host/(?P<sn>[^/]+)/', server_handler),
   url(r'^host/', server_handler),
)
