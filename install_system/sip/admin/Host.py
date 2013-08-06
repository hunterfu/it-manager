# -*- coding: utf8 -*-
from django.contrib import admin
from django.conf import settings
from sip.models import Network, KsTemp, Host
import os, re
# actions in batch
   
def reinstall(self, request, queryset):  
    select_file_path = "/tftpboot/pxelinux.cfg/"
    for host in queryset:
        if not host.mac:
            self.message_user(request, u'主机sn号（%s）的信息仍未上传' % host.sn)
            continue
        select_file = select_file_path + "01-" + host.mac.lower()
        if os.path.exists(select_file):
            os_version = host.ks_temp.ks_os_version
            f = open(select_file,'r')
            content = f.read()
            content = content.replace("default local", "default install")
            content = re.sub("kernel .*/vmlinuz", "kernel "+os_version+"/vmlinuz", content)
            content = re.sub("initrd=.*/initrd.img", "initrd="+os_version+"/initrd.img", content)
            f.close()
            f = open(select_file, 'w')
            f.write(content)
            f.close()
            host.status = 1
            host.save()
        else:
            self.message_user(request, u'选单文件%s不存在' % select_file)
reinstall.short_description = u"重新安装所选的主机"

def allocate_free_ip(self, request, queryset):
    subnet = request.REQUEST['subnet']
    network = Network.objects.get(subnet=subnet)
    scan_network(network)
    for host in queryset:
        nic = host.nic_set.get(eth_no=0)
        nic.ip = get_free_ip_and_use(subnet)
        nic.save()
allocate_free_ip.short_description = u"分配IP"

def get_free_ip_and_use(subnet):
    network = Network.objects.get(subnet=subnet)
    ip = Ip.objects.filter(network=network, status='F')[:1][0]
    ip.status = 'U'
    ip.save()
    return ip.ip_addr

def modify_os_version(self, request, queryset):
    kt_name = request.REQUEST['ks_temp']
    kt = KsTemp.objects.get(ks_temp_name=kt_name)
    queryset.update(ks_temp=kt)
modify_os_version.short_description = u"修改选定主机的安装模板"

def delete_all_select_host(self, request, queryset):
    select_file_path = "/tftpboot/pxelinux.cfg/"
    for host in queryset:
        print queryset
        if host.mac:
            select_file = select_file_path + "01-" + host.mac.lower()
            print select_file
       	    if os.path.exists(select_file):
                print "1"
                os.remove(select_file)
    queryset.delete()
delete_all_select_host.short_description = u"删除所选的主机（同时删除选单文件）"


class HostAdmin(admin.ModelAdmin):
    
    if settings.PRO_ENV == 'P':
        list_display = ('hostname', 'sn_oob', 'mac', 'show_status','list_ksTemp',  'list_nic', )
    elif settings.PRO_ENV == 'T':
        list_display = ('hostname', 'sn_oob', 'mac', 'show_status','list_ksTemp',  'list_nic', 'preinstall_button', 'install_button', 'show_vm_process_button')
    #list_display_links = ('host_ip',)
    list_filter = ('status',)
    #form = MyHostAdminForm
    #list_editable = ('mac', 'status')
    actions = [allocate_free_ip, reinstall, modify_os_version, delete_all_select_host]

    def get_actions(self, request):
	actions = super(HostAdmin, self).get_actions(request)
	del actions['delete_selected']
   	return actions
    search_fields = ['sn', 'hostname']
    #filter_horizontal = ('host_ip',)


admin.site.register(Host, HostAdmin)
