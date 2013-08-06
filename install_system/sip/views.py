from django.shortcuts import *
from django.conf import settings
from sip import Host, Ip, KsModule, KsModule_KsTemp, Log, Nic, Network
import csv , socket, struct, re, pexpect
import logging, subprocess
from my_util import *

script_tmpdir = "/mnt/xen_install_tmp"
# Create your views here.

def xen_preinstall(request,host_sn):
    sa_pla = "http://bsl.alipay.net/admin.php?q=xen&c=list&s=&hostname=&phyhost=%s&ip1=&postition=0" % (host_sn)
    h = Host.objects.get(sn=host_sn)
    nics = h.nic_set.all().order_by("eth_no")
    nic = nics[0]
    ip = nic.ip
    if ip == None:
        ip = nics[1].ip
	if ip == None:
	    return None
    print "preinstall the ip:%s host:%s" % (ip, h.hostname)
    ssh_cmd = ["ssh", "root@%s" % (ip), "mkdir -p " + script_tmpdir]
    p = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE)
    string = p.stdout.read()
    ssh_cmd = ["ssh", "root@%s" % (ip), "mount sysinstall.alipay.net:/home/sysinstall/reborn "+ script_tmpdir]
    p = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE)
    string += p.stdout.read()
    ssh_cmd = ["ssh", "root@%s" % (ip), "sh %s/xen/postinfo_sc.sh" % (script_tmpdir)]
    p = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE)
    string += p.stdout.read()
    ssh_cmd = ["ssh", "root@%s" % (ip), "umount "+ script_tmpdir]
    p = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE)
    string += p.stdout.read()
    # return HttpResponse(string, content_type='text/plain') 
    return redirect(sa_pla)

def show_xen_process(request, host_sn):
    h = Host.objects.get(sn=host_sn)
    nics = h.nic_set.all().order_by("eth_no")
    nic = nics[0]
    ip = nic.ip
    if ip == None:
        ip = nics[1].ip
	if ip == None:
	    return None
    ssh_cmd = ["ssh", "root@%s" % (ip), "mkdir -p " + script_tmpdir]
    p = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE)
    string = p.stdout.read()
    ssh_cmd = ["ssh", "root@%s" % (ip), "cat /tmp/xen_install/log/install.log "]
    p = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE)
    process_msg = p.stdout.read()
    return HttpResponse(process_msg, content_type='text/plain') 

def xen_install(request, host_sn):
    h = Host.objects.get(sn=host_sn)
    nics = h.nic_set.all().order_by("eth_no")
    nic = nics[0]
    ip = nic.ip
    if ip == None:
        ip = nics[1].ip
	if ip == None:
	    return None
    ssh_cmd = ["ssh", "root@%s" % (ip), "mkdir -p " + script_tmpdir]
    p = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE)
    string = p.stdout.read()
    ssh_cmd = ["ssh", "root@%s" % (ip), "mount sysinstall.alipay.net:/home/sysinstall/reborn "+ script_tmpdir]
    p = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE)
    ssh_cmd = ["ssh", "root@%s" % (ip), "sh %s/crhan_install_xen.sh -i 48_32" % (script_tmpdir)]
    print "vm(s) is installed in %s with ip:%s" % (h.hostname, ip)
    p = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE)
    string = p.stdout.read()
    print "test_string = " + string
    return HttpResponse("<html><head><title>installed</title></head><body>%s</body></html>" % (string)) 
   
def show_log(request):
    cmd = ["cat", "/home/admin/django/log/flup.log"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    log = p.stdout.read()
    return HttpResponse(log, content_type='text/plain')



