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
import pysqlite2.dbapi2 as sqlite
from common import *
"""
for extjs 4 
"""

# Create instance of FieldStorage 
form = cgi.FieldStorage() 
page = form.getvalue('page')
limit = form.getvalue('limit')
start = form.getvalue('start')
refresh = form.getvalue('refresh')

def show_list():
    myData = [
        ['3m Co',                               71.72, 0.02,  0.03,  '9/1 12:00am'],
        ['Alcoa Inc',                           29.01, 0.42,  1.47,  '9/1 12:00am'],
        ['Altria Group Inc',                    83.81, 0.28,  0.34,  '9/1 12:00am'],
        ['American Express Company',            52.55, 0.01,  0.02,  '9/1 12:00am'],
        ['American International Group, Inc.',  64.13, 0.31,  0.49,  '9/1 12:00am'],
        ['AT&T Inc.',                           31.61, -0.48, -1.54, '9/1 12:00am'],
        ['Boeing Co.',                          75.43, 0.53,  0.71,  '9/1 12:00am'],
        ['Wal-Mart Stores, Inc.',               45.45, 0.73,  1.63,  '9/1 12:00am']
    ]
 
    return_json = {"successproperty":"true","totalProperty":7,'root':[]}
    for item in myData:
        row_data = {}
        row_data['company'] = item[0]
        row_data['price'] = item[1]
        row_data['change'] = item[2]
        row_data['pctChange'] = item[3]
        row_data['lastChange'] = item[4]
        return_json['root'].append(row_data)
    return json.dumps(return_json)
    #return json.dumps(myData)

def show_stock_list():
    """
    显示程序自动筛选的股票列表
    """
    stock_list = get_stock_list()
    return_json = {"successproperty":"true","totalProperty":len(stock_list),'root':[]}
    for item_dict in stock_list:
        return_json['root'].append(item_dict)
    return json.dumps(return_json)


print "Content-Type: application/json\n"
print show_stock_list()
#print show_list()
