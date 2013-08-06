# -*- coding:utf-8 -*-
from django.db import models
import datetime

class Log(models.Model):
    class Meta:
        app_label = 'sip'
        verbose_name="日志"
	verbose_name_plural="日志"
	ordering = ["-time"]
    
    record = models.TextField(verbose_name='日志内容')
    time = models.DateTimeField(default=datetime.datetime.now)
    

    def set_record(self, log):
        self.record = log
        self.save()
 
