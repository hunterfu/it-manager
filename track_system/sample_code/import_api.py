#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = 0.1

import urllib,urllib2,sys
from pprint import pprint
from sys import argv
import os,sys
import commands
import re
import datetime
def post(url, data):  
    req = urllib2.Request(url)  
    data = urllib.urlencode(data)  
    #enable cookie  
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())  
    response = opener.open(req, data)  
    return response.read()  

def format_rack(val):
    """ format rack and rack_no """
    # rack
    ret = None
    if val.isdigit():
        ret =  "%02d" % int(val)
        return ret
    mo=re.match(r'(\w)(\d+)',val)
    if mo:
        alpha = mo.group(1)
        digit = mo.group(2)
        ret = "%s%02d" % (alpha,int(digit))
        return ret
    return val

def format_hostname(rack,rack_no):
    """ format hostname """
    hname = "xen-d0%s%s-vlan-b.idc" %(rack,rack_no)
    return hname



import_file_name = None
split_tag = None
try:
    import_file_name = argv[1]
except Exception,e:
    print "please set import file"
    exit(1)

try:
    split_tag = argv[2]
except:
    pass

base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
im_file = "%s/%s" % (base_dir,import_file_name)


fd = open(im_file)
content_list = fd.readlines()
fd.close()

# get import field from header(first line)
import_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
header_line = content_list.pop(0)
import_field_key = header_line.strip().split(",")
if split_tag:
    import_field_key = header_line.strip().split()
for line in content_list:
    line = line.strip()
    if not line: continue
    import_field_val = line.split(",")
    if split_tag:
        import_field_val = line.split()
    import_dict = {}
    i = 0
    for k in import_field_key:
        try:
            val = import_field_val[i]
            if val:
                if k in ['rack','rack_no']:
                    val = format_rack(val)
                import_dict[k] = val
        except:
            pass
        i = i + 1
    try:
        if not import_dict.has_key('hostname'):
            import_dict['hostname']= format_hostname(import_dict['rack'].lower(),import_dict['rack_no'].lower())
    except:
        pass

    #try:
    #    if not import_dict.has_key('batch'):
    #        import_dict['batch']=  import_time
    #except:
    #    pass
    # 
    #url_str= "&".join(["%s=%s" % (k, v) for k, v in import_dict.items()])
    #print url_str
    #url = "http://127.0.0.1:8000/api/host/"
    #print import_dict
    #sys.exit()
    #continue
    url = "http://localhost/api/host/"
    print import_dict['sn'],
    print post(url,import_dict)

