# -*- coding: utf8 -*-
from sip.models import KsModule
from django.shortcuts import *

def get_ks_module(request):
    km_id = request.REQUEST['id']
    if km_id == "":
        return HttpResponse('', content_type='text/plain')
    try:
        km = KsModule.objects.get(id=km_id)
    except KsModule.DoesNotExist:
        return HttpResponse('不存在这个模块', content_type='text/plain')
    return HttpResponse(km.content, content_type='text/plain')
