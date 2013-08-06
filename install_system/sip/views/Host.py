# -*- coding: utf8 -*-
from sip.models import Host, Nic, Log, KsTemp,Network
from django.shortcuts import *
from django.conf import settings
from sip.my_utils import *
import os, re

def list_ks(temp_name):
    kt = KsTemp.objects.get(ks_temp_name=temp_name)
    ks_modules = kt.ks_key.all().order_by("ks_no")
    ks_content = ""
    for km in ks_modules:
        ks_content = ks_content + km.content + "\n"
    ks_content = ks_content.replace("\r\n", "\n")
    return ks_content


def pxe(request):
    tag = request.REQUEST["tag"]
    sn = request.REQUEST["sn"]
    mac = request.REQUEST["mac"]
    
    actions = {
        "1":tag1,
        "2":tag2,
        "3":tag3
        }
    return actions.get(tag)(sn, mac)

def tag1(sn,mac):
    try:
        h = Host.objects.get(sn=sn)
    except Host.DoesNotExist:
        Log().set_record(u'fansi平台接受了一条不存在sn为%s的记录，请确认' % sn)
        return HttpResponse("None")
    h.mac = mac
    h.status = 1
    h.save()
    os_version = h.ks_temp.ks_os_version
    nic = Nic.objects.get(host=h, eth_no='0')
    nic.mac = mac
    nic.save()
    server_ip = settings.SERVER_IP
    f = open("/tftpboot/pxelinux.cfg/" + "01-" + mac.lower(),'w')
    f.write("prompt 1\ndefault install\ntimeout 10\nlabel install\nkernel "+os_version+"/vmlinuz\nappend initrd="+os_version+"/initrd.img ksdevice=eth0 ks=http://"+ server_ip +"/pxe?mac="+ mac +"&&tag=2&&sn="+ sn +" devfs=nomount ramdisk_size=9216 nofb\n\nlabel local\nlocalboot 1\n")
    f.close()
    return HttpResponse("None")


def tag2(sn,mac):
    c = Host.objects.filter(status=3).count()
    h = Host.objects.get(sn=sn)
    if h == None:
       raise Exception("主机记录不存在")
    if c >= int(settings.INSTALL_Q_NO):
        try:
            ks = KsTemp.objects.get(ks_temp_name='wait_for_q')
        except KsTemp.DoesNotExist:
            raise Exception("Ks模板'wait_for_q不存在，该模板用于让超过安装队列的安装请求等待")
        ks_cont = list_ks(ks)
        h.status = 2
        h.save()
        return HttpResponse(ks_cont, content_type='text/plain') 
    ks = h.ks_temp.ks_temp_name
    h.status = 3
    h.save()
    ks_cont = list_ks(ks)
    return HttpResponse(ks_cont, content_type='text/plain') 

def tag3(sn,mac):
    mac_cfg_dir="/tftpboot/pxelinux.cfg/"
    h = Host.objects.get(sn=sn)
    h.status=7
    h.save()
    mac = h.mac
    mac = mac.lower()
    os_version = h.ks_temp.ks_os_version
    f = open(mac_cfg_dir + "01-" + mac)
    mac_select_file = f.read()
    mac_select_file = mac_select_file.replace("default install", "default local")
    mac_select_file = re.sub("kernel .*/vmlinuz", "kernel "+os_version+"/vmlinuz", mac_select_file)
    mac_select_file = re.sub("initrd=.*/initrd.img", "initrd="+os_version+"/initrd.img", mac_select_file)
    f.close()
    f = open(mac_cfg_dir + "01-" + mac,"w")
    f.write(mac_select_file)
    f.close()
    
    return HttpResponse(mac_select_file)

def mac(request, mac):
    mac = mac.__getslice__(0, len(mac)-1)
    h = Host.objects.get(mac=mac)
    return HttpResponse(h.hostname)

    
def import_host(request):
    file = request.FILES['csv_hosts']
    reader = upfile_to_reader(file)
    flag = 0 
    
    print settings.PRO_ENV
    if settings.PRO_ENV == 'P':
        for discard_1, hostname_t, nic1_ip_t, nic2_ip_t, discard_2, discard_3, discard_4, discard_5, discard_6, discard_7,  nic1_port_t, nic2_port_t,discard_8, discard_9, sn_t, discard_10, discard_11, discard_12, discard_13, discard_14, discard_15, discard_16, discard_17, discard_18 in reader:
            try:
                h = Host.objects.get(sn=sn_t)
                h.hostname = hostname_t
                h.nic_set.all().delete()
                h.save()
                nic1 = Nic(eth_no=0, switch_port=nic1_port_t, ip=nic1_ip_t, host=h)
                nic2 = Nic(eth_no=1, switch_port=nic2_port_t, ip=nic2_ip_t, host=h)
                nic1.save()
                nic2.save()
            except Host.DoesNotExist:
                #kt = KsTemp.objects.get(ks_temp_name=ks_temp_t)
                h = Host(hostname=hostname_t,
                    sn=sn_t,
                    #ks_temp=kt,
                )
                h.save()
                nic1 = Nic(eth_no=0, switch_port=nic1_port_t, ip=nic1_ip_t, host=h)
                nic2 = Nic(eth_no=1, switch_port=nic2_port_t, ip=nic2_ip_t, host=h)
                nic1.save()
                nic2.save()
    elif settings.PRO_ENV == 'T':
        for discard_1, hostname_t, nic1_ip_t, nic2_ip_t, discard_2, discard_3, discard_4, discard_5, discard_6, discard_7,  nic1_port_t, nic2_port_t,discard_8, oob_url_t, sn_t, discard_10, discard_11, discard_12, discard_13, discard_14, discard_15, discard_16  in reader:
            try:
                h = Host.objects.get(sn=sn_t)
                h.hostname = hostname_t
                h.oob_url = oob_url_t
                h.nic_set.all().delete()
                h.save()
                nic1 = Nic(eth_no=0, switch_port=nic1_port_t, ip=nic1_ip_t, host=h)
                nic2 = Nic(eth_no=1, switch_port=nic2_port_t, ip=nic2_ip_t, host=h)
                nic1.save()
                nic2.save()
            except Host.DoesNotExist:
                #kt = KsTemp.objects.get(ks_temp_name=ks_temp_t)
                h = Host(hostname=hostname_t,
                    sn=sn_t,
                    oob_url=oob_url_t
                    #ks_temp=kt,
                )
                h.save()
                nic1 = Nic(eth_no=0, switch_port=nic1_port_t, ip=nic1_ip_t, host=h)
                nic2 = Nic(eth_no=1, switch_port=nic2_port_t, ip=nic2_ip_t, host=h)
                nic1.save()
                nic2.save()
    else:
        raise Exception("the variety PRO_ENV has not been set correctly in settings file")
        
    return redirect('/admin/sip/host/')

def get_host_conf(request, mac):
    #mac = mac.__getslice__(0, len(mac)-1)
    mac = mac.replace(":","-")
    try: 
        h = Host.objects.get(mac=mac)
    except:
            return HttpResponse("none", content_type='text/plain') 
    nic = h.nic_set.get(eth_no=0)
    def ip_to_n(ip):
        return socket.ntohl(struct.unpack("I",socket.inet_aton(ip))[0])

    ip_n = ip_to_n(nic.ip)   
    networks = Network.objects.all()
    for network in networks:
	if ip_to_n(network.ip_start) <= ip_n and ip_to_n(network.ip_end) >= ip_n:
	    n = network
    str = "HOSTNAME=" + h.hostname +"\n"+\
	"IPADDR=" + nic.ip +"\n"+\
	"NETMASK=" + n.netmask +"\n"+\
	"NETWORK=" + n.subnet +"\n"+\
	"BROADCAST=" + n.broadcast +"\n"+\
 	"GATEWAY=" + n.gateway +"\n"+\
	"VLAN=" + n.vlan_id.__str__()
    return HttpResponse(str, content_type='text/plain') 


def count(request):
    c = Host.objects.filter(status=3).count()
    return HttpResponse(c, content_type='text/plain')

def set_install_max_no(request):
    no = request.REQUEST['max']
    settings.INSTALL_Q_NO=no
    return HttpResponse('')
    
def get_install_max_no(request):
    return HttpResponse(settings.INSTALL_Q_NO, content_type='text/plain')


