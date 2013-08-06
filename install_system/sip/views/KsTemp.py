# -*- coding: utf8 -*-
from sip.models import KsTemp
from django.shortcuts import *

def list_ks(temp_name):
    kt = KsTemp.objects.get(ks_temp_name=temp_name)
    ks_modules = kt.ks_key.all().order_by("ks_no")
    ks_content = ""
    for km in ks_modules:
        ks_content = ks_content + km.content + "\n"
    ks_content = ks_content.replace("\r\n", "\n")
    return ks_content

def get_ks_temps(request):
    kts = KsTemp.objects.all()
    html = ''
    for kt in kts:
        ks_temp_name = kt.ks_temp_name
        html += '<option value="%s">%s</option>' % (ks_temp_name, ks_temp_name)
    return HttpResponse(html, content_type='text/plain')

def list_ks_temp(request, temp_name):
    ks_content = list_ks(temp_name)
    return HttpResponse(ks_content, content_type='text/plain') 


