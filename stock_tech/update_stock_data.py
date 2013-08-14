#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = 0.1

from lib import stock
import sys
import os
import shutil
import pickle
import re
import time
#import pysqlite2.dbapi2 as sqlite
import sqlite3 as sqlite
import getopt
from operator import itemgetter
from decimal import *
import urllib
import json
import fpformat
import subprocess
import datetime
import string
import pprint
import commands
"""
定期更新股票历史交易数据
"""

def export_history_data(base_dir,symbol):
    """ 导出历史交易数据 """
    symbol = symbol.upper()
    cache_dir = "%s/trade_db" % (base_dir)
    db_file = "%s/%s" % (cache_dir,symbol)
    #export_file = "/home/hua.fu/geniustrader/data/%s" % symbol
    export_dir =  "%s/stock_history_data" %(base_dir)
    if not os.path.exists(export_dir):
        os.system("mkdir -p %s" % export_dir)
    export_file = "%s/%s.txt" % (export_dir,symbol)
    stock_FILE = open(export_file,"w")
    
    (db_cursor,cx,tag) = connect_trade_db(db_file)
    cx.text_factory=str
    sql="select s_date,s_open,s_high,s_low,s_close,s_volume from stock order by s_date"
    db_cursor.execute(sql)
    rs = db_cursor.fetchall()
    if len(rs) == 0:
        return
    for item in rs:
        s_date = item[0]
        s_open = item[1]
        s_high = item[2]
        s_low = item[3]
        s_close = item[4]
        s_volume = item[5]
        line = "%s\t%s\t%s\t%s\t%s\t%s\n" %(s_open,s_high,s_low,s_close,s_volume,s_date) 
        stock_FILE.writelines(line)  
    stock_FILE.close()
    #cmd = "/bin/sqlite %s 'select s_date,s_open,s_high,s_low,s_close,s_volume from stock order by s_date' |/bin/sed -e 's/|/  /g' >%s.txt" % (db_file,export_file)
    #(status,output) = commands.getstatusoutput(cmd)
    # if status != 0: 
        # print "======== Error ========="
        # print output

def delete_stock(db_cursor,cx,stock_symbol):
    """根据stock_symbol 删除"""
    sql_cmd = "delete from stock where stock_symbol = '%s'" %(stock_symbol)
    db_cursor.execute(sql_cmd)
    cx.commit()
    print "Delete %s success" % (stock_symbol.upper())


def connect_trade_db(db_file):
    """
    连接历史交易数据库
    """
    if os.path.isfile(db_file) and os.path.getsize(db_file) != 0:
        cx = sqlite.connect(db_file)
        cu = cx.cursor()
        return (cu,cx,"old")
    else:
        cx = sqlite.connect(db_file)
        cu = cx.cursor()
        cu.execute('''create table stock(
            id integer primary key,
            s_date varchar(50),
            s_open varchar(10),
            s_high varchar(10),
            s_low varchar(10),
            s_close varchar(10),
            s_volume INTEGER
            )''')
        return (cu,cx,"new")

def update_trade_db(db_cursor,cx,symbol,tag):
    """ 更新股票历史交易数据 """
    # 新建数据库
    if tag =="new":
        current_time = datetime.datetime.now().strftime("%Y%m%d")
        one_year_ago = (datetime.datetime.now() - datetime.timedelta(days=3000)).strftime("%Y%m%d")
        data = stock.get_historical_prices(symbol,one_year_ago,current_time)
        last_close_price = 0
        if not data:
            print "update_trade_db Error : NO HISTORY DATA,PLEASE CHECK,SYMBOL = %s" % (symbol)
            return 
        for item in data:
            s_date = item[0]
            s_open = item[1]
            s_high = item[2]
            s_low = item[3]
            s_close = item[4]
            #s_close = item[6]   # adj close 拆股或者合股
            s_volume = item[5]
            if not s_volume.isdigit(): continue
            if float(s_close) == 0:
                if symbol.find(".") != -1:
                    (real_symbol,suffix) = symbol.split(".")
                    if suffix.lower() in ['ss','sz']:
                        s_open = last_close_price
                        s_close = last_close_price
                        s_high = last_close_price
                        s_low = last_close_price
            else:
                last_close_price = s_close

            sql_cmd = 'insert into stock values(NULL,"%s","%s","%s","%s","%s",%s)' % (s_date,s_open,s_high,s_low,s_close,s_volume)
            db_cursor.execute(sql_cmd)
        cx.commit()
    elif tag =="old":
        # 判断最大日期数
        sql_cmd = "select max(s_date),s_close from stock" 
        db_cursor.execute(sql_cmd)
        rs = db_cursor.fetchone()
        max_date = rs[0]
        last_close_price = rs[1]
        if max_date:
            #current_time = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y%m%d")
            current_time = datetime.datetime.now().strftime("%Y%m%d")
            last_update_time = datetime.datetime.strptime(max_date,"%Y-%m-%d")
            want_update_time = (last_update_time + datetime.timedelta(days=1)).strftime("%Y%m%d")
        else:
            #current_time = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
            current_time = datetime.datetime.now().strftime("%Y%m%d")
            want_update_time = (datetime.datetime.now() - datetime.timedelta(days=3000)).strftime("%Y%m%d")
    
        #want_update_time = last_update_time.strftime("%Y%m%d")
        #if datetime.datetime.now().weekday() in [0,6]: return  
        #if want_update_time <= current_time:
        if want_update_time < current_time:
            data = stock.get_historical_prices(symbol,want_update_time,current_time)
            if data:
                for item in data:
                    s_date = item[0]
                    s_open = item[1]
                    s_high = item[2]
                    s_low = item[3]
                    s_close = item[4]
                    #s_close = item[6]   # adj close 拆股或者合股
                    s_volume = item[5]
                    if not s_volume.isdigit(): continue
                    if float(s_close) == 0:
                        if symbol.find(".") != -1:
                            (real_symbol,suffix) = symbol.split(".")
                            if suffix.lower() in ['ss','sz']:
                                s_open = last_close_price
                                s_close = last_close_price
                                s_high = last_close_price
                                s_low = last_close_price
                    sql_cmd = 'insert into stock values(NULL,"%s","%s","%s","%s","%s",%s)' % (s_date,s_open,s_high,s_low,s_close,s_volume)
                    #print "sql_cmd = " + sql_cmd
                    db_cursor.execute(sql_cmd)
                cx.commit()

def update_trade_data(base_dir,symbol):
    """ 更新交易数据 """
    cache_dir = "%s/trade_db" % (base_dir)
    if not os.path.exists(cache_dir): 
        os.system("mkdir -p %s" % cache_dir)
    symbol = symbol.upper()
    db_file = "%s/%s" % (cache_dir,symbol)
    (db_cursor,cx,tag) = connect_trade_db(db_file)
    cx.text_factory=str
    update_trade_db(db_cursor,cx,symbol,tag)
    return (db_cursor,cx)
   
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

def get_avg_volume(db_cursor,cx,day=30):
    """ 得到30天平均交易量"""
    rs = None
    sql_cmd = "select s_volume from stock stock order by s_date desc limit %s" % (day)
    db_cursor.execute(sql_cmd)
    rs = db_cursor.fetchall()
    result = []
    for item in rs:
        result.append(item[0])

    avg_volume = sum(result) / day
    return avg_volume

def get_last_price(db_cursor,cx):
    """ 得到最近一天的收盘价格 """
    rs = None
    sql_cmd = "select s_close from stock stock order by s_date desc limit 1" 
    db_cursor.execute(sql_cmd)
    rs = db_cursor.fetchone()
    if not rs:
        print "Error = Last close price is null,please check"
        return 0
    return rs[0]

def last_trade_date(db_cursor,cx):
    """ 判断是否停盘 """    
    sql_cmd = "select max(s_date) from stock"
    db_cursor.execute(sql_cmd)
    rs = db_cursor.fetchone()
    max_date = rs[0]
    if max_date:
        dayago_45 = (datetime.datetime.now() - datetime.timedelta(days=45)).strftime("%Y%m%d")
        last_update_time = datetime.datetime.strptime(max_date,"%Y-%m-%d").strftime("%Y%m%d")
        #want_update_time = last_update_time.strftime("%Y%m%d")
        if last_update_time < dayago_45:
            print "The Stock Has Stop Trading..."
            return False
    return True

def calculate_cost(db_cursor,cx,days):
    """ 
    估算持仓成本价格
    """
    sql_cmd = "select s_date,s_close,s_volume from stock order by s_date DESC limit %s" % days
    db_cursor.execute(sql_cmd)
    rs = db_cursor.fetchall()

    if len(rs) == 0:
        #print "Symbol = %s : ==== No record,please check ====" % (symbol)
        return (0,0)
    sum_trade_money = 0
    sum_trade_volume = 0
    avg_trade_volume = 0
    for item in rs:
        (s_date,s_close,s_volume)  = item
        sum_trade_money = Decimal(s_close) * s_volume + sum_trade_money
        sum_trade_volume = sum_trade_volume + s_volume 
        
    #avg_cost_price = round(sum_trade_money / sum_trade_volume,3)
    if sum_trade_volume == 0:
        avg_cost_price = 0
        avg_trade_volume = 0
    else:
        avg_cost_price = sum_trade_money / sum_trade_volume
        avg_trade_volume = sum_trade_volume / days
    #return (avg_cost_price,avg_trade_volume)
    print "day = %s\tavg_cost = %.6s\tavg_volume=%s" % (days,avg_cost_price,convert_number_to_money(avg_trade_volume))
    
def convert_number_to_money(number):
    """
    格式化输出
    """
    number = str(number)
    new_list = []
    new_str = ""
    stage = 0
    for i in number[::-1]:
        stage +=1
        new_str += i
        if len(new_str) == 3:
            new_list.append(new_str[::-1])
            new_str = ""
        elif stage == len(number):
            new_list.append(new_str[::-1])
    convert_done_number = string.join(new_list[::-1],",")
    return convert_done_number

def new_stock(db_cursor,cx):
    """ 判断是否是新股 """
    sql_cmd = "select count(*) from stock"
    db_cursor.execute(sql_cmd)
    rs = db_cursor.fetchone()
    count = rs[0]
    if count <= 90:
        return True
    return False

def iterate_stock(db_cursor,cx,base_dir,symbol=None,title=None,stock_region=None):
    """ 
    遍历股票列表数据库，更新股票历史交易数据
    """
    sql = ""
    if symbol:
        sql = "select * from stock where stock_symbol='%s'" % symbol
    else:
        time_now = int(time.time())
        #last_update_time = time_now - 86400
        last_update_time = time_now - 3600 * 12
        #last_update_time = time_now - 1800
        #last_update_time = time_now
        if stock_region:
            stock_region = stock_region.upper()
            sql = "select * from stock where stock_tradedb_lastupdate_time <= %s and stock_country = '%s' order by stock_tradedb_lastupdate_time,stock_symbol" % (last_update_time,stock_region)
        else:
            sql = "select * from stock where stock_tradedb_lastupdate_time <= %s order by stock_tradedb_lastupdate_time,stock_symbol" % (last_update_time)
    db_cursor.execute(sql)
    rs = db_cursor.fetchall()
    if DEBUG: print "sql = %s" % sql
    # print title
    if len(rs) == 0 and symbol:
        print "%s not in db,add to db" % symbol
        sql_cmd = None
        if title:
            sql_cmd = 'insert into stock (id,stock_symbol,stock_title,stock_tradedb_lastupdate_time) values(NULL,"%s","%s",0)' % (symbol,title)
        else:
            sql_cmd = 'insert into stock (id,stock_symbol,stock_tradedb_lastupdate_time) values(NULL,"%s",0)' % (symbol)
        #print "insert into sql_cmd = %s" % sql_cmd
        db_cursor.execute(sql_cmd)
        cx.commit()
        
    elif len(rs)>0:
        count = len(rs)
        for item in rs:
            stock_id = item[0]
            exchange = item[1]
            symbol = item[3]
            if DEBUG: 
                print "[%s] DEBUG SYMBOL = %s" % (count,symbol)
                count = count -1
            stock_tradedb_lastupdate_time = item[5] or 0
            #if symbol.find("/") != -1 or symbol.find("^") != -1 or symbol.find("*") != -1 or symbol.find("-") != -1:
            if symbol.find("/") != -1 or symbol.find("*") != -1 or symbol.find("-") != -1:
                delete_stock(db_cursor,cx,symbol)
                continue      
            symbol = symbol.upper()
            try:
                (stock_cursor,stock_cx) = update_trade_data(base_dir,symbol)
                last_close_price = get_last_price(stock_cursor,stock_cx)
                avg_volume = get_avg_volume(stock_cursor,stock_cx,50)
                stop_trade = last_trade_date(stock_cursor,stock_cx)
                newstock = new_stock(stock_cursor,stock_cx)
                if DEBUG:
                    calculate_cost(stock_cursor,stock_cx,30)
                    calculate_cost(stock_cursor,stock_cx,60)
                    calculate_cost(stock_cursor,stock_cx,120)
                    calculate_cost(stock_cursor,stock_cx,250)
                stock_cx.close()
                
                if not stop_trade:
                    delete_stock(db_cursor,cx,symbol)
                    continue
                if float(last_close_price) <= 0.5:
                    print "last close price <=0.5" 
                    #next_check_time = int(time.time()) + 24 * 3600 * 2
                    #sql_cmd = "update stock set stock_tradedb_lastupdate_time = %s where stock_symbol='%s'" % (next_check_time,symbol)
                    #db_cursor.execute(sql_cmd)
                    #cx.commit()
                    delete_stock(db_cursor,cx,symbol)
                    continue
                if  avg_volume == 0 or avg_volume < 50000:
                    print "The Last 30 Trade Day Avg Volume = 0 or avg_volume < 50000"
                    delete_stock(db_cursor,cx,symbol)
                    continue
                if float(last_close_price) <=5: 
                    # 一个月后再检查
                    print "last_close_price <= 5 , one week later to check"
                    next_check_time = int(time.time()) + 24 * 3600 * 7
                    sql_cmd = "update stock set stock_tradedb_lastupdate_time = %s where stock_symbol='%s'" % (next_check_time,symbol)
                    db_cursor.execute(sql_cmd)
                    cx.commit()
                    export_history_data(base_dir,symbol)
                    continue
                if  avg_volume < 500000: 
                    # 2周后检查
                    print "Stock avg_Volume < 500000 , one month later to check"
                    next_check_time = int(time.time()) + 24 * 3600 * 30 
                    sql_cmd = "update stock set stock_tradedb_lastupdate_time = %s where stock_symbol='%s'" % (next_check_time,symbol)
                    db_cursor.execute(sql_cmd)
                    cx.commit()
                    export_history_data(base_dir,symbol)
                    continue 
                if newstock:
                    print "new stock ,one month later to check"
                    next_check_time = int(time.time()) + 24 * 3600 * 30
                    sql_cmd = "update stock set stock_tradedb_lastupdate_time = %s where stock_symbol='%s'" % (next_check_time,symbol)
                    db_cursor.execute(sql_cmd)
                    cx.commit()
                    continue

                next_check_time = int(time.time())
                sql_cmd = "update stock set stock_tradedb_lastupdate_time = %s where stock_symbol='%s'" % (next_check_time,symbol)
                db_cursor.execute(sql_cmd)
                cx.commit()
                export_history_data(base_dir,symbol)

            except IOError,e:
                print "Symbol = %s ,Network Reset, Error = %s"  % (symbol,e)
                next_check_time = int(time.time()) + 24 * 3600 * 2
                sql_cmd = "update stock set stock_tradedb_lastupdate_time = %s where stock_symbol='%s'" % (next_check_time,symbol)
                db_cursor.execute(sql_cmd)
                cx.commit()
                time.sleep(10)
            except Exception,e:
                print "Symbol = %s Error = %s" % (symbol,e)

def get_home_path():
	"""
	得到用户主目录
	"""
	homedir = os.environ.get('HOME')
	if homedir:
		return homedir
	else:
		homedir = "%s%s" % (os.environ.get('HOMEDRIVE'),os.environ.get('HOMEPATH'))
	return homedir
                      
def usage():
    print '''
Usage: monitor_stock.py [options...]
Options: 
    -e/--exchane                        : Exchange Name 
    -t/--title                          : Stock title
    -s/--symbol                         : Stock symbol
    -d/--debug                          : run in debug mode 
    -D/--delete                         : delete stock
    -r/--region                         : the special region of stock [CHINA|US|HK]
    -h/--help                           : this help info page
    
Example:
    # default is checking all stock which in monitor db
    monitor_stock.py
    # debug special stock
    monitor_stock.py -s ras
    # setting stock support line and resistance_line
    monitor_stock.py -s ras -l 2.44,2.48
    # setting stock channel,maybe uptrend or downtrend
    monitor_stock.py -s ras -c 2010-07-01,2010-07-02,2010-07-03 
    '''
    

def main():
    """ main function """
    global DEBUG,base_dir
    DEBUG = False
    base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    #homedir = get_home_path()
    #base_dir = "%s/stock_tech" % (homedir)
    #base_dir = /home/hua.fu/geniustrader
    cache_dir = "%s/tmp" % (base_dir)
    stock_db = "%s/db/stock_db" % (base_dir)
   
    try:
        opts, args = getopt.getopt(sys.argv[1:],'Ddhe:t:s:l:c:r:')
    except getopt.GetoptError:
        usage()
        sys.exit()
    
    #各个变量保存
    stock_title = ""
    stock_symbol = ""
    stock_exchange = ""
    stock_line = ""
    stock_channel =""
    stock_region =""

    is_delete = False
    is_print = False
    #global tradedb_lastupdate_time
    
    for opt, arg in opts: 
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt == '-t':
            stock_title = arg
        elif opt == '-s':
            stock_symbol = arg
            stock_symbol = stock_symbol.upper()
        elif opt == '-e':
            stock_exchange = arg
        elif opt == '-d':
            DEBUG = True
        elif opt == '-p':
            is_print = True
        elif opt == '-r':
            stock_region = arg
        elif opt == '-D':
            is_delete = True
              
    db_cursor = None
    cx = None
    (db_cursor,cx) = connect_db(stock_db)
    cx.text_factory=str

   
    if stock_symbol and is_delete:
        try:
            delete_stock(db_cursor,cx,stock_symbol)
        except Exception,e:
            print "setting line data format wrong,ErrMsg = %s" % (e)
            usage()
            sys.exit()
    elif stock_symbol:
        iterate_stock(db_cursor,cx,base_dir,stock_symbol,stock_title)
    elif stock_region:
        iterate_stock(db_cursor,cx,base_dir,stock_region=stock_region)
    else:
        iterate_stock(db_cursor,cx,base_dir)
  
    cx.close()    
if __name__ == "__main__":
    main()
    #print get_home_path()

