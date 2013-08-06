# -*- coding: utf8 -*-
from django.db import models

class KsModule(models.Model):
    class Meta:
        app_label = 'sip'
	verbose_name="ks模块"
	verbose_name_plural="ks模块"
    KsNoChoice = ((1, 'base'), (2, 'partition'), (3, 'packages'), (4, 'pre-script'), (5, 'post-script'))
    ks_no = models.IntegerField(max_length=1, choices=KsNoChoice, verbose_name="ks顺序")
    ks_module_name = models.CharField(max_length=20,unique=True, verbose_name="ks模块名")
    content = models.TextField(verbose_name="ks模块内容")

    def __unicode__(self):
        return self.KsNoChoice[self.ks_no-1][1] + '--' + self.ks_module_name


