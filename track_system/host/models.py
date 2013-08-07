# -*- coding: utf8 -*-
from django.db import models

class Server(models.Model):
    sn = models.CharField(max_length=30, verbose_name="主机序列号")
    hostname = models.CharField(max_length=30, verbose_name="主机名",blank = True,null = True)
    status = models.CharField(max_length=30, verbose_name="安装状态",blank = True,null = True)
    ip = models.CharField(max_length=30, verbose_name="主机IP",null=True,blank=True)
    oob_ip = models.CharField(max_length=30, verbose_name="带外IP",null=True,blank=True)
    idc = models.CharField(max_length=30, verbose_name="机房",null=True,blank=True)
    rack = models.CharField(max_length=30, verbose_name="机柜",null=True,blank=True)
    rack_no = models.CharField(max_length=30, verbose_name="机柜号",null=True,blank=True)
    comment = models.TextField(null=True,blank=True)
    
    class Meta:
        verbose_name="主机"
        verbose_name_plural="主机"

    def __unicode__(self):
        return self.hostname

