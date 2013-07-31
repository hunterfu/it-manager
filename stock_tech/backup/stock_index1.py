#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import datetime
import fpformat
from lib import stock

def connect_db(db_file):
    """
    连接数据库
    """
    if os.path.isfile(db_file):
        if int(time.time()) - int(os.stat(db_file).st_mtime) >= 86400:
            cx = sqlite.connect(db_file)
            cu = cx.cursor()
            return (cu,cx,"old")
        else:
            cx = sqlite.connect(db_file)
            cu = cx.cursor()
            return (cu,cx,"nothing")
    else:
        #create
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
    """ 更新交易数据库 """
    # 新建数据库
    if tag =="new":
        current_time = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
        one_year_ago = (datetime.datetime.now() - datetime.timedelta(days=300)).strftime("%Y%m%d")
        data = stock.get_historical_prices(symbol,one_year_ago,current_time)
        for item in data:
            s_date = item[0]
            s_open = item[1]
            s_high = item[2]
            s_low = item[3]
            s_close = item[4]
            s_volume = item[5]
            if not s_volume.isdigit(): continue
            sql_cmd = 'insert into stock values(NULL,"%s","%s","%s","%s","%s",%s)' % (s_date,s_open,s_high,s_low,s_close,s_volume)
            #print "sql_cmd = " + sql_cmd
            db_cursor.execute(sql_cmd)
            cx.commit()
    elif tag =="old":
        # 判断最大日期数
        sql_cmd = "select max(s_date) from stock" 
        db_cursor.execute(sql_cmd)
        rs = db_cursor.fetchone()
        max_date = rs[0]
        if max_date:
            current_time = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
            last_update_time = datetime.datetime.strptime(max_date,"%Y-%m-%d")
            want_update_time = (last_update_time + datetime.timedelta(days=1)).strftime("%Y%m%d")
        else:
            current_time = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
            want_update_time = (datetime.datetime.now() - datetime.timedelta(days=300)).strftime("%Y%m%d")
    
        #want_update_time = last_update_time.strftime("%Y%m%d")
        if want_update_time <= current_time:
            data = stock.get_historical_prices(symbol,want_update_time,current_time)
            if data:
                for item in data:
                    s_date = item[0]
                    s_open = item[1]
                    s_high = item[2]
                    s_low = item[3]
                    s_close = item[4]
                    s_volume = item[5]
                    if not s_volume.isdigit(): continue
                    sql_cmd = 'insert into stock values(NULL,"%s","%s","%s","%s","%s",%s)' % (s_date,s_open,s_high,s_low,s_close,s_volume)
                    #print "sql_cmd = " + sql_cmd
                    db_cursor.execute(sql_cmd)
                    cx.commit()

def get_trade_data(days):
    """ 得到固定天数的交易数据 """
    sql_cmd = "select s_date,s_close,s_volume from stock order by s_date DESC limit %s" % days
    db_cursor.execute(sql_cmd)
    rs = db_cursor.fetchall()
    return rs

def get_support_line():
    """ 取得支撑线 """
    record_count = 60
    last_low_val = 0
    last_low = {}
    rs = get_trade_data(record_count)
    s_rs = sorted(rs, key=lambda result: result[1])
    print s_rs


def get_resistance_line():
    """ 取得阻力线 """
    record_count = 65
    last_low_val = 0
    last_low = {}
    last_high_val = 0
    last_high = {}
    rs = get_trade_data(record_count)


# 定义变量 
base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
cache_dir = "%s/trade_db" % (base_dir)
symbol =""
try:
    symbol = sys.argv[1]
except Exception,e: 
    symbol = "RAS"
symbol = symbol.upper()
db_file = "%s/%s" % (cache_dir,symbol)
(db_cursor,cx,tag) = connect_db(db_file)
cx.text_factory=str
update_trade_db(db_cursor,cx,symbol,tag)
# 分析股票 横盘时间(股价 +- 10%),正负叠加应该接近于0 才能说明是横盘
rs = get_trade_data(260)
l_date = []
l_close = []
l_volume = []
for item in rs:
    (s_date,s_close,s_volume)  = item
    l_date.append(s_date)
    l_close.append(s_close)
    l_volume.append(s_volume)

# 计算平均交易量
day_count = 0
volume_sum = 0
price_sum = 0
record_count = len(l_date)
result_list = []
avg_volume = 0
avg_price = 0
change_sum = 0
avg_change = 0 #涨跌 正负叠加应该接近于0 才能说明是横盘
last_trade_price = 0 #最后一个交易日价格
for index in range(record_count):
    s_date = l_date[index] 
    s_close = l_close[index]
    s_volume = l_volume[index]
    if last_trade_price == 0: last_trade_price = Decimal(s_close)

    # 计算涨跌幅
    #print "index = %s , record_count = %s" % (index,record_count)
    if index+1 != record_count: 
        s_close_day_flat = l_close[index + 1]
        change = (Decimal(s_close) - Decimal(s_close_day_flat))/Decimal(s_close_day_flat) * 100
        change = Decimal(str(round(change, 2)))
    else:
        change = 0

    # 价格在一定周期的均线价格 +- 3% 浮动
    if last_trade_price * Decimal(str("0.95")) <= Decimal(s_close) <= last_trade_price * Decimal(str("1.05")):
        result_list.append((s_date,s_close,s_volume,change))
        day_count = day_count + 1;
        volume_sum = volume_sum + s_volume
        price_sum = Decimal(s_close) + price_sum 
        change_sum = change_sum + change
        #last_trade_price = Decimal(s_close)
    else:
        # 横盘时间不能太短，小于3天无效
        if day_count < 3: 
            last_trade_price = Decimal(s_close)
            volume_sum = 0
            price_sum = 0
            change_sum = 0
            result_list = []
            day_count = 0
            continue
        elif day_count != 0:
            avg_volume = volume_sum / day_count
            avg_price = Decimal(str(round(price_sum / day_count,3)))
            break

# 输出结果
try:
    debug = sys.argv[2]
    for index in range(len(result_list)):
        (s_date,s_close,s_volume,change) = result_list[index]
        print "%s = %s = %s = %s avg_volume = %s avg_price = %s change_sum = %s" % (s_date,s_close,s_volume,change,avg_volume,avg_price,change_sum)
except Exception,e: 
    pass
h_day_count = len(result_list)
(s_date,s_close,s_volume,change) = result_list[0] # 取得最近一个交易日的数据
volume_increase_time = Decimal(str(round(Decimal(s_volume) / avg_volume,2)))
#output = "volume_increase_time = %s avg_price= %s change_sum= %s h_day= %s" % (volume_increase_time,avg_price,change_sum,h_day_count)
output = "%s,%s,%s,%s" % (volume_increase_time,avg_price,change_sum,h_day_count)

if Decimal(s_volume) > avg_volume and Decimal(s_close) > avg_price:
    print "%s,横盘可能启动" % output
else:
    print "%s,横盘待观察中" % output
