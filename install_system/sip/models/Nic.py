# -*- coding: utf8 -*-
from django.db import models
from sip.models.Host import Host
from sip.models.Network import  Network
from sip.my_utils import ip_to_n

class Nic(models.Model): 
    class Meta:
        app_label = "sip"
	verbose_name="网卡"
	verbose_name_plural="网卡"
    eth_no = models.CharField(max_length=10)
    mac = models.CharField(max_length=20, blank=True, null=True, verbose_name="网卡地址")
    switch_port = models.CharField(max_length=20)
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    ip = models.IPAddressField(blank=True, verbose_name="网卡IP")

    def get_vlan(self):
        if len(self.ip) == 0:
            return ""
        ip_n = ip_to_n(self.ip)   
        networks = Network.objects.all()
        for network in networks:
    	    if ip_to_n(network.ip_start) <= ip_n and ip_to_n(network.ip_end) >= ip_n:
    	        n = network
    	        return n.vlan_id


