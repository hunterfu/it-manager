#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = 0.1

import urllib,urllib2,sys
from pprint import pprint
from sys import argv
import os
import commands

def post(url, data):  
    req = urllib2.Request(url)  
    data = urllib.urlencode(data)  
    #enable cookie  
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())  
    response = opener.open(req, data)  
    return response.read()  

import_file_name = None
try:
    import_file_name = argv[1]
except Exception,e:
    print "please set import file"
    exit(1)

base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
im_file = "%s/%s" % (base_dir,import_file_name)


fd = open(im_file)
content_list = fd.readlines()
fd.close()

# get import field from header(first line)
import_field_key = content_list.pop(0).split()
for line in content_list:
    line = line.strip()
    if not line: continue
    import_field_val = line.split()
    import_dict = {}
    i = 0
    for k in import_field_key:
        try:
            val = import_field_val[i]
            import_dict[k] = val
        except:
            pass
        i = i + 1
    # 
    #url_str= "&".join(["%s=%s" % (k, v) for k, v in import_dict.items()])
    #print url_str
    url = "http://127.0.0.1:8000/api/host/"
    print import_dict['sn'],
    print post(url,import_dict)

