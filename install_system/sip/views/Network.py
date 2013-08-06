# -*- coding: utf8 -*-
import csv
from sip.models import Network, Ip
from django.shortcuts import *

def import_network(request):
    file = request.FILES['csv_networks']
    import csv
    reader = csv.reader(file)
    except_msg = ""
    for vlan_id_t, vlan_name_t, subnet_t, ip_start_t, ip_end_t, gateway_t, netmask_t, broadcast_t in reader:
        n = Network(subnet=subnet_t,
                ip_start=ip_start_t,
                ip_end=ip_end_t,
                gateway=gateway_t,
                netmask=netmask_t,
                broadcast=broadcast_t,
                vlan_id=vlan_id_t,
                vlan_name=vlan_name_t
                )
        try:
            n.save()
        except Exception, e:
            except_msg += str(e)+ "vlan_id = %s" % (vlan_id_t) +'\n'
            continue
    if len(except_msg) != 0:
        return HttpResponse(except_msg, content_type='text/plain') 
    return redirect('/admin/sip/network/')

def scan_all_networks(request):
    networks = Network.objects.all()
    p=re.compile('(\d+\.\d+\.\d+\.\d+)')
    for n in networks:
        scan_network(n)
    return HttpResponse("扫描完毕", content_type='text/plain')
#        args = '-sP' + ' ' + n.ip_start + '-' + n.ip_end.split('.')[-1]
#	nmap_result = pexpect.run('nmap ' + args)
#	ip_list = p.findall(nmap_result)
#        list_start = n.ip_start.split('.')
#        list_end = n.ip_end.split('.')
#	ip_start = list_start[-1]
#	ip_end = list_end[-1]
#        start = int(ip_start)
#        end = int(ip_end)
#	while start <= end:
#            list_start[-1] = str(start)
#            ip = '.'.join(list_start)
#	    if ip not in ip_list:
#	        try:
#	            ip = Ip.objects.get(ip_addr=ip)
#		    if ip.status == 'A':
#		        ip.status = 'F'
#                    elif ip.status == 'U':
#		        try:
#		            Nic.objects.get(ip=ip.ip_addr)
#			except Nic.DoesNotExist:
#			    ip.status = 'F'
#		    ip.save()
#		except Ip.DoesNotExist:
#	            i = Ip(ip_addr=ip,
#	                network=n,
#	                status='F'
#	                )
#	            i.save()
#            start+=1
#	for ip in ip_list:
#	    i = Ip(ip_addr=ip,
#	        network=n,
#		status='A'
#		)
#	    i.save()

def scan_network(n):
    p=re.compile('(\d+\.\d+\.\d+\.\d+)')
    args = '-sP' + ' ' + n.ip_start + '-' + n.ip_end.split('.')[-1]
    nmap_result = pexpect.run('nmap ' + args)
    ip_list = p.findall(nmap_result)
    list_start = n.ip_start.split('.')
    list_end = n.ip_end.split('.')
    ip_start = list_start[-1]
    ip_end = list_end[-1]
    start = int(ip_start)
    end = int(ip_end)
    while start <= end:
        list_start[-1] = str(start)
        ip = '.'.join(list_start)
        if ip not in ip_list:
            try:
                ip = Ip.objects.get(ip_addr=ip)
    	        if ip.status == 'A':
    	            ip.status = 'F'
                elif ip.status == 'U':
    	            try:
    	                Nic.objects.get(ip=ip.ip_addr)
    		    except Nic.DoesNotExist:
    		        ip.status = 'F'
    	        ip.save()
    	    except Ip.DoesNotExist:
                i = Ip(ip_addr=ip,
                    network=n,
                    status='F'
                    )
                i.save()
        start+=1
    for ip in ip_list:
        i = Ip(ip_addr=ip,
            network=n,
    	status='A'
    	)
        i.save()



