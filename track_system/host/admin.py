# -*- coding: utf8 -*-
from django.contrib import admin
from django.conf import settings
from host.models import Server
import os, re
   

class ServerAdmin(admin.ModelAdmin):
    list_display = ('sn', 'hostname', 'ip', 'oob_ip','idc','rack','rack_no')
    list_filter = ('status','idc','rack')
    list_editable = ('hostname','ip')
    search_fields = ['sn','hostname','ip']


admin.site.register(Server, ServerAdmin)
