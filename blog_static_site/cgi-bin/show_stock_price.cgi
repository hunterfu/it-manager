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
symbol_list = form.getvalue('symbol_list')

def show_price_list():
    """
    显示程序自动筛选的股票列表
    """
    stock_list = get_symbol_list();
    if len(stock_list) == 1:
        stock_price = get_stock_price(stock_list[0])
        return_json = {"successproperty":"true","totalProperty":len(stock_price),'root':[]}
        for item_dict in stock_price:
            return_json['root'].append(item_dict)
        return json.dumps(return_json)

def get_symbol_list():
    """
    解码symbol list
    """
    symbol = eval(symbol_list);
    return symbol

print "Content-Type: application/json\n"
print show_price_list()
