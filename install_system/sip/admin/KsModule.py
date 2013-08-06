from django.contrib import admin
from django import forms
from sip.models import KsModule
from django.db import models


class KsModuleAdmin(admin.ModelAdmin):
    list_display = ('ks_module_name', 'content',)
    list_display_links = ('ks_module_name', 'content')
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea},
    }
    ordering = ["ks_no"]

admin.site.register(KsModule, KsModuleAdmin)
