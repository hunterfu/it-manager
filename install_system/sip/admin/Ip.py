from django.contrib import admin
from sip.models import Ip

class IpAdmin(admin.ModelAdmin):
    list_display = ('ip_addr', 'network', 'status', 'last_update_time')
    search_fields = ['ip_addr', ]
    list_filter = ('status',)

admin.site.register(Ip, IpAdmin)
