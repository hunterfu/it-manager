from sip.models import Nic
from django.contrib import admin

class NicAdmin(admin.ModelAdmin):
    list_display = ('host', 'eth_no', 'mac', 'ip', 'switch_port')
    prepopulated_fields = { 'mac' : ['mac'] } 


admin.site.register(Nic, NicAdmin)
