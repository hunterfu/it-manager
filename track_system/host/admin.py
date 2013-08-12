# -*- coding: utf8 -*-
from django.contrib import admin
from django.conf import settings
from host.models import Server
import os, re
   

class ServerAdmin(admin.ModelAdmin):
    list_display = ('sn', 'hostname', 'ip', 'oob_ip','status','ks_temp','idc')
    list_filter = ('status','idc','ks_temp')
    #list_editable = ('hostname','ip')
    search_fields = ['sn','hostname','ip']


admin.site.register(Server, ServerAdmin)
