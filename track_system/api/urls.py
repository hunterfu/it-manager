from django.conf.urls import *
from piston.resource import Resource
from api.handlers import ServerHandler

server_handler = Resource(ServerHandler)

urlpatterns = patterns('',
   url(r'^host/', server_handler),
)
