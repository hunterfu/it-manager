#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = 0.1
""" 根据google的股票筛选器来更新股票列表 """

from lib import stock
import sys
import os
import shutil
import pickle
import re
import time
import pysqlite2.dbapi2 as sqlite
import getopt
from operator import itemgetter
from decimal import *
import urllib
import json
import fpformat
import subprocess
import csv
from urllib import FancyURLopener
from random import choice
from pprint import pprint


def request_one(cache_file,country):
    """ get data from google """

    if country == "US":
        stock_exchange = '((exchange == "NYSE") | (exchange == "NASDAQ") | (exchange == "AMEX"))'
        stock_volume = " (volume >= 50000)"
        q = "[%s & %s]" % (stock_exchange,stock_volume)
        q = urllib.quote(q)
        url = 'http://www.google.com/finance?gl=us&hl=en&output=json&start=0&num=9000&noIL=1&q=%s&restype=company' % q
    elif country == "CHINA":
        stock_exchange = '((exchange == "SHA" | exchange == "SHE") & (shareclass == "A" | shareclass == "Q"))' 
        stock_volume = " (volume >= 50000)"
        q = "[%s & %s]" % (stock_exchange,stock_volume)
        q = urllib.quote(q)
        url = 'http://www.google.com.hk/finance?output=json&start=0&num=9000&noIL=1&q=%s&restype=company' % q
    elif country == "HK":
        stock_exchange = '(exchange == "HKG")' 
        stock_volume = " (volume >= 50000)"
        q = "[%s & %s]" % (stock_exchange,stock_volume)
        q = urllib.quote(q)
        url = 'http://www.google.com.hk/finance?output=json&start=0&num=9000&noIL=1&q=%s&restype=company' % q


    f = urllib.urlopen(url)
    content = f.readlines()
    fout = open(cache_file, "w")
    for line in content:
        fout.write(line)
    fout.close()
    return True

def request_two(cache_file,country):
    """ get data from google """

    if country == "US":
        stock_exchange = "((exchange:NYSE) OR (exchange:NASDAQ) OR (exchange:AMEX))"
        stock_volume = " (Volume > 50000 | Volume = 50000)"
        q = "%s [%s & %s]" % (stock_exchange,stock_volume)
        q = urllib.quote(q)
        url = 'http://www.google.com/finance?&gl=us&hl=en&output=json&start=0&num=9000&noIL=1&q=%s&restype=company' % q
    elif country == "CHINA":
        stock_exchange = '((exchange:SHA) OR (exchange:SHE) & (shareclass == "A" | shareclass == "Q"))' 
        stock_volume = " (Volume > 50000 | Volume = 50000)"
        q = "%s [%s & %s]" % (stock_exchange,stock_volume)
        q = urllib.quote(q)
        url = 'http://www.google.com.hk/finance?output=json&start=0&num=9000&noIL=1&q=%s&restype=company' % q
    elif country == "HK":
        stock_exchange = '(exchange:HKG)'
        stock_volume = " (Volume > 50000 | Volume = 50000)"
        q = "%s [%s & %s]" % (stock_exchange,stock_volume)
        q = urllib.quote(q)
        url = 'http://www.google.com.hk/finance?output=json&start=0&num=9000&noIL=1&q=%s&restype=company' % q

    f = urllib.urlopen(url)
    content = f.readlines()
    fout = open(cache_file, "w")
    for line in content:
        fout.write(line)
    fout.close()
    return True
    
def request(cache_file,country):
    if not os.path.isfile(cache_file) or (int(time.time()) - int(os.stat(cache_file).st_mtime) >= 86400):
        have_data = False
        method_list = ['one','two']
        for method in method_list:
            func = "request_%s(cache_file,'%s')" % (method,country)
            eval(func)
            json_data=open(cache_file).read()
            data = eval(json_data)
            stock_data_list = data['searchresults']
            if len(stock_data_list) != 0: 
                have_data = True
                return stock_data_list
        if not have_data:
            print "Get Stock list From google Failed,Please Check"
            sys.exit(1)
    else:
        json_data=open(cache_file).read()
        data = eval(json_data)
        stock_data_list = data['searchresults']
        return stock_data_list

def get_stock_list(stock_data_list):
    """
    read data from json file and update to sqlite db
    """
    #json_data=open(cache_file).read()
    #data = eval(json_data)

    #print "num_company_results = " + data['num_company_results']
    stock_list = [] 
    # one stock
    #stock_data_list = data['searchresults']
    for stock_data in stock_data_list:
        stock_dict = {}
        stock_dict['symbol'] = stock_data['ticker']
        stock_dict['title'] = stock_data['title']
        stock_dict['exchange'] = stock_data['exchange']
        stock_list.append(stock_dict)
    return stock_list 

def connect_db(db_file):
    """
    股票列表数据库  
    """
    if os.path.isfile(db_file):
        cx = sqlite.connect(db_file)
        cu = cx.cursor()
        return (cu,cx)
    else:
        cx = sqlite.connect(db_file)
        cu = cx.cursor()
        cu.execute('''
            create table stock(
            id integer primary key,
            exchange_name varchar(20),
            stock_title varchar(50),
            stock_symbol varchar(20) UNIQUE,
            stock_country varchar(100),
            stock_tradedb_lastupdate_time NUMERIC DEFAULT 0
            )''')
        return (cu,cx)


def update_db(db_cursor,cx,stock_list,country):
    """ update db from json file """
    for stock_dict in stock_list:
        # determin record is already in db or not
        stock_exchange = stock_dict['exchange']
        stock_symbol = stock_dict['symbol']
        stock_title = stock_dict['title']
        if stock_symbol.find("/") != -1 or stock_symbol.find("^") != -1 or stock_symbol.find("*") != -1 or stock_symbol.find("-") != -1:
            continue
        stock_country = country
        if country == 'CHINA':
            if stock_exchange == 'SHA': stock_symbol = "%s.SS" % (stock_symbol)
            if stock_exchange == 'SHE': stock_symbol = "%s.SZ" % (stock_symbol)
        elif  country == 'HK':
            stock_symbol = "%s.HK" % (stock_symbol)

        print "exchange = %s , stock_symbol= %s , stock_title = %s" % (stock_exchange,stock_symbol,stock_title)
        #continue

        sql_cmd = "select count(*) from stock where stock_symbol = '%s'" % (stock_symbol)
        db_cursor.execute(sql_cmd)
        rs = db_cursor.fetchone()
        rs_count = rs[0]
        try:
            if not rs_count:
                sql_cmd = 'insert into stock values(NULL,"%s","%s","%s","%s",%d)' % (stock_exchange,stock_title,stock_symbol,stock_country,0)
                db_cursor.execute(sql_cmd)
            else:
                sql_cmd = 'update stock set stock_title="%s",stock_country="%s",exchange_name="%s" where stock_symbol = "%s"' % (stock_title,stock_country,stock_exchange,stock_symbol)
                db_cursor.execute(sql_cmd)
            cx.commit()
        except Exception,e:
            print "SQL = %s"  % (sql_cmd)
            print "Symbol = %s Error = %s" % (stock_symbol,e)


def main():
    """ main function """
    base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    cache_dir = "%s/tmp" % (base_dir)
    db_file = "%s/db/stock_db" % (base_dir)
    (db_cursor,cx) = connect_db(db_file)
    cx.text_factory=str
    region = ['US','HK','CHINA']
    #region = ['HK','CHINA']
    for country in region:
        cache_file = "%s/%s" % (cache_dir,"google_json_%s" % (country))
        stock_data_list = request(cache_file,country)
        update_db(db_cursor,cx,get_stock_list(stock_data_list),country)

    cx.close()

if __name__ == "__main__":
    main()




