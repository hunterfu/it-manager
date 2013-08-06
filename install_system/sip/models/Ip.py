# -*- coding:utf-8 -*-
from django.db import models
from sip.models.Network import Network
import datetime

class Ip(models.Model):
    class Meta:
        app_label = 'sip'
	verbose_name = 'Ip'
	verbose_name_plural = 'Ips'
    status_choices = (('allocate', 'A'),('allocate', 'A'),('allocate', 'A'),)
    ip_addr = models.IPAddressField(verbose_name="ip地址")
    network = models.ForeignKey(Network)
    last_update_time = models.DateTimeField(default=datetime.datetime.now)
    status = models.CharField(max_length=1)
    
    def save(self):
	self.last_update_time = datetime.datetime.now()
        super(Ip,self).save()


