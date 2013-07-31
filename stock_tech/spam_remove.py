#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = 0.1

import urllib,urllib2,sys
from pprint import pprint
from BeautifulSoup import BeautifulSoup
from sys import argv


try:
    remove_ip = argv[1]
except Exception,e:
    print "Please Input Ip which you want remove"
    sys.exit(1)

url = "http://www.mail-abuse.com/cgi-bin/nph-dul-remove?%s" % (remove_ip)
referer_url = "http://www.mail-abuse.com/cgi-bin/lookup?ip_address=%s" % (remove_ip)
content = urllib.urlopen(url).read()
soup = BeautifulSoup(content)
#html_data = open('test.html','r').read()
#soup = BeautifulSoup(html_data)
#print soup.prettify()
b = soup.findAll('input')
#a = b.pop()
#print a
#[(n['name'], n['value']) for n in soup.findAll('input')]
post_data = {}
for item in soup.findAll('input'):
    #input_type = item.attrs[0][1]
    #if input_type == "HIDDEN":
    #    name = item.attrs[1][1]
    #    value = item.attrs[2][1]
    #    print "name = %s value = %s" % (name,value)
    if item['type'] == "HIDDEN":
        name = item['name']
        value = item['value']
        print "name = %s value = %s" % (name,value)
        post_data[name]  = value


# post data

post_data['email'] = 'xianjun.zhuxj@alibaba-inc.com'
post_data['message-body']='Hi my smtp gateway outbond addresses are from 110.75.192.1 to 110.75.192.254,they are official,please remove all of them Thanks'
post_data['realname'] = 'xianjun.zhuxj'

#pprint(post_data)

post_url = "http://www.mail-abuse.com/cgi-bin/dul-mailer.cgi"
data = urllib.urlencode(post_data)
req = urllib2.Request(post_url, data)
req.add_header('Referer',referer_url)
response = urllib2.urlopen(req)
the_page = response.read()

print the_page


