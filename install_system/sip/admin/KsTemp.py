from sip.models import kmkt, KsTemp
from django.contrib import admin

class KsTempAdmin(admin.ModelAdmin):
    #form = MyKsTempAdminForm

    list_display = ('ks_temp_name', 'list_ks_cont', 'list_ks', 'ks_temp_dscpt')
    filter_horizontal = ('ks_key',)
    '''
    fieldsets = (
            (None, {
             'fields':('KsTempName', 'KsKey'),
             'classes':('collapse'),
             }),
            )
    '''
    inlines = (kmkt,)


admin.site.register(KsTemp, KsTempAdmin)
