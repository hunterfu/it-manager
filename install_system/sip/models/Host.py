# -*- coding: utf8 -*-
from django.db import models
from sip.models.KsTemp import KsTemp

class Host(models.Model):
    class Meta:
        app_label = 'sip'
	verbose_name="主机"
	verbose_name_plural="主机"
    # os_version_choices = (('rh57-64',"rh57-64"),('rh56-64',"rh56-64"),('rh48-64',"rh48-64"),('rh48-32',"rh48-32"),('rh48-32',"rh48-32"))
    hostname = models.CharField(max_length=30, verbose_name="主机名")
    sn = models.CharField(max_length=30, verbose_name="主机序列号")
    mac = models.CharField(max_length=20,blank=True,null=True, verbose_name="mac地址")
    status = models.IntegerField(null=True, blank=True, verbose_name="安装状态")
    # is_physical = models.BooleanField(verbose_name="是否为物理机")
    # host_machine = models.ForeignKey("Host", null=True, blank=True, verbose_name="宿主机")
    # os_version = models.CharField(max_length=10, verbose_name='系统版本', choices=os_version_choices)
    ks_temp = models.ForeignKey(KsTemp,null=True, blank=True, verbose_name="ks模版")
    oob_url = models.CharField(blank=True, null=True, max_length=30)
    
    class SnDoesNotExist(Exception):
        pass
        

    def __unicode__(self):
        return self.hostname

    def sn_oob(self):
        print self.oob_url
        if self.oob_url != "" and self.oob_url != None:
            return '<a href="http://%s" target="_Blank">%s</a>'%(self.oob_url, self.sn)
        return '%s'%(self.sn)
    sn_oob.allow_tags=True
    sn_oob.short_description = u"主机序列号（点击进入带外管理）"

    def list_ksTemp(self):
        if self.ks_temp == None:
            return "未分配安装模板"
        return '<a href="/ks_temp/%s" target="_Blank">%s</a>'%(self.ks_temp, self.ks_temp)
    list_ksTemp.allow_tags=True
    list_ksTemp.short_description = u"安装模版"


    def list_nic(self):
        host_nics = self.nic_set.all()
        if not len(host_nics):
            return ""
        host_nics_order = host_nics.order_by("eth_no")
        colume = ""
        eth0_pk = host_nics_order[0].pk
        for nic in host_nics_order:
            colume += '{eth%s IP:%s,VL:%s,SP:%s}' % (nic.eth_no, nic.ip, nic.get_vlan(), nic.switch_port)
        return '<a href="/admin/sip/nic/%s">%s</a>'% (eth0_pk, colume)
    list_nic.allow_tags=True
    list_nic.short_description = u"主机网卡"

    def show_status(self):
        status_show = "未定义状态码"
	if self.status == None:
	    status_show = "未安装"
	elif self.status == 1:
	    status_show = "上传信息"
	elif self.status == 2:
	    status_show = "队列等待"
	elif self.status == 3:
	    status_show = "正在安装"
	elif self.status == 7:
	    status_show = "安装完毕"
        return status_show
    show_status.short_description = u"主机状态"

    def install_button(self):
	#  if self.is_physical:
        return '<!--<select id="vm_version" ><option value="48_64">48_64</option><option value="55_64">55_64</option></select>--><a id="install_%s" href="/install_xen/%s" target="_Blank"></a><button onclick="document.getElementById(\'install_%s\').click();">%s</button'%(self.sn, self.sn, self.sn, u"安装虚拟机")
            # return '<form action=\"install_xen/%s\" ><select id="vm_version" ><option value="48_64">48_64</option><option value="55_64">55_64</option></select><button type=\"submit\" >%s</button"</form>' % (self.sn, u"安装虚拟机")
    install_button.allow_tags=True
    install_button.short_description = u"安装虚拟机"

    def preinstall_button(self):
	# if self.is_physical:
        return '<a id="preinstall_%s" href="/preinstall_xen/%s" target="_Blank"></a><button onclick="document.getElementById(\'preinstall_%s\').click();">%s</button'%(self.sn, self.sn, self.sn, u"导入虚拟机信息")
    preinstall_button.allow_tags=True
    preinstall_button.short_description = u"导入虚拟机信息"

    def show_vm_process_button(self):
	# if self.is_physical:
        return '<a id="process_%s" href="/process_xen/%s" target="_Blank"></a><button onclick="document.getElementById(\'process_%s\').click();">%s</button'%(self.sn, self.sn, self.sn, u"查看虚拟机安装日志")
    show_vm_process_button.allow_tags=True
    show_vm_process_button.short_description = u"查看虚拟机安装日志"
 
