# -*- coding:utf-8 -*-
from django.db import models
from django.contrib import admin
from django.conf import settings
from django.utils.translation import ugettext_lazy, ugettext as _
from sip.models import *
from django import forms
from django.http import HttpResponse
import os.path, re, csv
from my_util import *

def export_all_select_host(modeladmin, request, queryset):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=hosts.csv'
    
    writer = UnicodeWriter(response, encoding='gb2312')
    # writer = csv.writer(response)
    flag = 0
    if settings.PRO_ENV == 'P':
        for h in queryset:
            if flag == 0:
    	        flag = 1
                writer.writerow([u"财产编码",u"主机名",u"网卡ip地址1",u"网卡ip地址2",u"",u"",u"",u"",u"",u"",u"网卡端口1",u"网卡端口2",u"",u"",u"机器序列号",u"",u"",u"",u"",u"",u"",u"",u"",u"",u"ks模板"])
    
            nics = h.nic_set.all().order_by("eth_no")
            writer.writerow(["",h.hostname, nics[0].ip, nics[1].ip, "","","","","","",  nics[0].switch_port, nics[1].switch_port,"", "",  h.sn,"", "", "", "", "", "", "", "", "", h.ks_temp.ks_temp_name])
    elif settings.PRO_ENV == 'T':
        for h in queryset:
            if flag == 0:
    	        flag = 1
                writer.writerow([u"财产编码",u"主机名",u"网卡ip地址1",u"网卡ip地址2",u"",u"",u"",u"",u"",u"",u"网卡端口1",u"网卡端口2",u"",u"",u"机器序列号",u"",u"",u"",u"",u"",u"",u"",u"ks模板"])
    
            nics = h.nic_set.all().order_by("eth_no")
            writer.writerow(["",h.hostname, nics[0].ip, nics[1].ip, "","","","","","",  nics[0].switch_port, nics[1].switch_port,"", "",  h.sn,"", "", "", "", "", "", "",  h.ks_temp.ks_temp_name])
    
    return response
export_all_select_host.short_description = u"导出所选的主机"
    
	
# register models in admin app
#class MyHostAdminForm(forms.ModelForm):
#    class Meta:
#        model = Host

#class MyKsTempAdminForm(forms.ModelForm):
#    #test = forms.ModelChoiceField(queryset=KsModule.objects.all())
#    class Meta:
#        model = KsTemp
#
#    def clean_name(self):
#        return self.cleaned_date["name"]




#
#    

