# -*- coding: utf8 -*-
from django.contrib import admin
from django.conf import settings
from host.models import Server
from django.http import HttpResponse
import os, re
import os.path, re, csv
from django.db.models import Q
import operator

class UnicodeWriter:
    def __init__(self,f,encoding='utf8'):
        self.writer = csv.writer(f)
        self.encoding = encoding

    def writerow(self, row):
        #self.writer.writerow([s.encode(self.encoding) for s in row])
        ret_list = []
        for s in row:
            if s: ret_list.append(s.encode(self.encoding))
            else: ret_list.append("")
        #self.writer.writerow([s.encode(self.encoding) for s in row if s])
        self.writer.writerow(ret_list)


def export_all_select_host(modeladmin, request, queryset):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=server.csv'

    writer = UnicodeWriter(response, encoding='utf8')
    # writer = csv.writer(response)
    writer.writerow(["sn","hostname","ip","oobip","status","SysProgress","AppProgress","comment",'rack','rack_no','idc'])
    for h in queryset:
        writer.writerow([h.sn,h.hostname,h.ip,h.oob_ip,h.status,"%s - %s" % (h.setupProgress,h.setupProgressMsg) ,"%s - %s" % (h.appProgress,h.appProgressMsg),h.comment,h.rack,h.rack_no,h.idc])
    return response

export_all_select_host.short_description = u"导出所选的主机"

def update_batch(self, request, queryset):
    for host in queryset:
        host.batch_check = 'complete'
        host.save()
    self.message_user(request, u'机器交付更新成功')

update_batch.short_description = u"将选中机器完成交付"

class ServerAdmin(admin.ModelAdmin):
    list_display = ('sn', 'hostname', 'ip', 'oob_ip','status','comment','idc','show_link')
    #list_display_links = ('sn','hostname')
    list_filter = ('status','idc','batch','batch_check')
    #list_editable = ('hostname','ip')
    search_fields = ['sn','hostname','ip','oob_ip']
    actions=[export_all_select_host,update_batch]
    def show_link(self, obj):
        if obj.aops_trackid:
            url = "http://aops.alibaba-inc.com/workflow/idc/view/?xdatatype=&INSTS=%s,customize,725320&actor=&state=finish" % (obj.aops_trackid)
            return u'<a href="%s" target=_blank>%s</a>' % (url,obj.aops_trackid)
        else:
            #html_table = u'<a href="JavaScript:window.open(\'%s\');">输入跟踪ID</a>' % ("http://www.alibaba.com")
            return u'<a href="%s" target="_blank" >输入跟踪ID</a>' % obj.id
            #return u'<a href="http://www.alibaba.com" target="_blank">输入跟踪ID</a>'
            #return u'<a href="http://www.alibaba.com" class="popup">输入跟踪ID</a>'
    show_link.short_description = 'Aops_Track'
    show_link.allow_tags = True
    #class Media:
        #js = ( "http://ajax.googleapis.com/ajax/libs/jquery/1.2.6/jquery.min.js",\
        #"http://ajax.googleapis.com/ajax/libs/jqueryui/1.5.2/jquery-ui.min.js",\
        #"/static/addonjs/jquery.popupWindow.js","/static/addonjs/my_popup.js")
        #js = ("http://ajax.googleapis.com/ajax/libs/jqueryui/1.5.2/jquery-ui.min.js","/static/addonjs/jquery.popupWindow.js")

    #list_display = ('sn', 'hostname', 'ip', 'oob_ip','status','comment','idc','show_link')
    #def queryset(self, request):
    #    qs = super(ServerAdmin, self).queryset(request)
    #    # probably there is a better way to extract this value this is just 
    #    # an example and depends on the type of the form field 
    #    data = request.GET
    #    if data.has_key('q'):
    #        query_string = data['q']
    #        predicates = [('sn', '6CU330216Q'), ('sn', '6CU330217B')]
    #        qq_list = [Q(x) for x in predicates]
    #        return qs.filter(reduce(operator.or_, qq_list))
    #        #return  qs.filter(sn='6CU330216Q')

    #        q_list = query_string.split()
    #        if len(q_list) >1:
    #            print q_list
    #            predicates = [('sn', '6CU330216Q'), ('sn', '6CU330217B')]
    #            qq_list = [Q(x) for x in predicates]
    #            #qs.filter(sn__in = q_list)
    #            #filter_dict = {'sn__in': ['6CU330216Q','6CU330217B']}
    #            #Listing.objects.filter(**filter_dict)
    #            #qs.filter(sn__in = ['6CU330216Q','6CU330217B'])
    #            #qs.filter(reduce(operator.or_, qq_list))
    #            #qs = qs.filter(Q(sn='6CU330216Q'))
    #            return  qs.filter(sn='6CU330216Q')
    #    return qs

admin.site.register(Server, ServerAdmin)
