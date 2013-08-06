# -*- coding: utf8 -*-
from django.db import models

class Network(models.Model):
    class Meta:
    	app_label = 'sip'
	verbose_name="网络"
	verbose_name_plural="网络"
    subnet = models.CharField(max_length=20, verbose_name="网络号")
    ip_start = models.IPAddressField(verbose_name="IP起始地址")
    ip_end = models.IPAddressField(verbose_name="IP结束地址")
    gateway = models.IPAddressField(verbose_name="网关")
    netmask = models.IPAddressField(verbose_name="子网掩码")
    broadcast = models.IPAddressField(verbose_name="广播地址")
    vlan_name = models.CharField(max_length=40, verbose_name="vlan名称")
    vlan_id = models.IntegerField(max_length=20, verbose_name="vlanID")

    def __unicode__(self):
        return self.ip_start + '~' + self.ip_end


