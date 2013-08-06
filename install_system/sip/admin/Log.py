# -*- coding: utf-8 -*- 
# 2012年 03月 02日 星期五 13:34:28 CST
from django.contrib import admin
from sip.models import Log

class LogAdmin(admin.ModelAdmin):
    list_display = ['record', 'time']

admin.site.register(Log, LogAdmin)
