# -*- coding: utf8 -*-
from django.db import models
#from sip.models.KsModule import KsModule
from KsModule import KsModule
from django.contrib.admin import TabularInline
from django.conf import settings

class KsTemp(models.Model):
    class Meta:
        app_label = 'sip'
	verbose_name="ks模版"
	verbose_name_plural="ks模版"
    os_version_tmp = []
    for os_version in settings.OS_VERSION:
        os_version_tmp.append((os_version,os_version))
    os_version_choices = tuple(os_version_tmp)    
    # os_version_choices = (('rh57-64',"rh57-64"),('rh56-64',"rh56-64"),('rh48-64',"rh48-64"),('rh48-32',"rh48-32"),('rh48-32',"rh48-32"))
    ks_temp_name = models.CharField(max_length=30,unique=True, verbose_name="ks模版名")
    ks_key = models.ManyToManyField(KsModule, through="KsModule_KsTemp", verbose_name="ks模版序列")
    #ks_key = models.CharField(max_length=30,unique=True, verbose_name="ks模名")
    ks_os_version = models.CharField(max_length=10, verbose_name="ks模板的OS版本", choices=os_version_choices)
    ks_temp_dscpt = models.TextField(verbose_name="ks模板描述")

    def list_ks(self):
        pass
        ks = ""
        for i in self.ks_key.order_by("ks_no"):
            ks = ks + i.__unicode__() + ","
        return ks.__getslice__(0, ks.__len__()-1)
    
    def list_ks_input(self):
        return ks_key
        #return ((1),(2))

    def list_ks_cont(self):
        return '<a href="/ks_temp/%s" target="_Blank">%s</a>'%(self.ks_temp_name, self.ks_temp_name)
    list_ks_cont.allow_tags=True
    list_ks_cont.short_description = u"查看ks"
        

    def __unicode__(self):
        return self.ks_temp_name

class KsModule_KsTemp(models.Model):
    class Meta:
        app_label = 'sip'
    ks_module = models.ForeignKey(KsModule, on_delete=models.PROTECT)
    ks_temp = models.ForeignKey(KsTemp)

class kmkt(TabularInline):
    class Meta:
        app_label = 'sip'
    model = KsModule_KsTemp
    extra = 5
    verbose_name=u'ks模块_ks模版关联'
    verbose_name_plural=u'包含的ks模块'
