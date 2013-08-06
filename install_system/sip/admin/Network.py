from django.contrib import admin
from sip.models import Network

class NetworkAdmin(admin.ModelAdmin):
    list_display = ('subnet', '__unicode__', 'gateway', 'netmask','broadcast', 'vlan_name', 'vlan_id')
    # list_display_links = ('gateway',)
    search_fields = ['subnet', 'vlan_name', 'vlan_id']


admin.site.register(Network, NetworkAdmin)
