# -*- coding: utf8 -*-
from django.db import models

class Server(models.Model):
    sn = models.CharField(max_length=30, verbose_name="主机序列号")
    hostname = models.CharField(max_length=50, verbose_name="主机名",blank = True,null = True)
    status = models.CharField(max_length=30, verbose_name="总进度",blank = True,null = True)
    app_state = models.CharField(max_length=50, verbose_name="应用状态",blank = True,null = True)
    ip = models.CharField(max_length=30, verbose_name="主机IP",null=True,blank=True)
    oob_ip = models.CharField(max_length=30, verbose_name="带外IP",null=True,blank=True)
    ks_temp = models.CharField(max_length=30, verbose_name="安装模板",null=True,blank=True)
    idc = models.CharField(max_length=30, verbose_name="机房",null=True,blank=True)
    rack = models.CharField(max_length=30, verbose_name="机柜",null=True,blank=True)
    rack_no = models.CharField(max_length=30, verbose_name="机柜号",null=True,blank=True)
    batch = models.CharField(max_length=50, verbose_name="安装批次",null=True,blank=True)
    batch_check = models.CharField(max_length=50, verbose_name="批次检查",default='check', editable=False)
    aops_trackid = models.CharField(max_length=10, verbose_name="AOPS跟踪ID",null=True,blank=True)
    setupProgress =  models.CharField(max_length=50, verbose_name="安装进度",blank = True,null = True)
    appProgress =  models.CharField(max_length=50, verbose_name="应用进度",blank = True,null = True)
    appProgressMsg =  models.CharField(max_length=250, verbose_name="应用消息",blank = True,null = True)
    setupProgressMsg =  models.CharField(max_length=250, verbose_name="安装消息",blank = True,null = True)

    last_update =  models.IntegerField(null=True)
    comment = models.TextField(null=True,blank=True)
    
    class Meta:
        verbose_name="主机"
        verbose_name_plural="主机"

    def __unicode__(self):
        return self.sn

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.last_update: self.last_update = 0
        return super(Server, self).save(*args, **kwargs)

