#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
from time import strftime,gmtime
import datetime
import commands
import re
import json
import cgi, cgitb 
"""
for extjs 4 show base info about stock 
"""

# Create instance of FieldStorage 
form = cgi.FieldStorage() 
page = form.getvalue('page')
limit = form.getvalue('limit')
start = form.getvalue('start')
symbol = form.getvalue('symbol')

def show_list():
    myData = [
       ['test1', 71.72,1.2,34.3],
       ['test2', 1.47,1.2,34.3],
    ]
    if symbol:
        myData = [['C', 71.72,1.2,34.3]]
 
    return_json = {"successproperty":"true","totalProperty":7,'root':[]}
    for item in myData:
        row_data = {}
        row_data['name'] = item[0]
        row_data['pe'] = item[1]
        row_data['eps'] = item[2]
        row_data['price'] = item[3]
        #row_data[item[0]] = item[1]
        return_json['root'].append(row_data)
    return json.dumps(return_json)
    #return json.dumps(myData)


print "Content-Type: application/json\n"
print show_list()
