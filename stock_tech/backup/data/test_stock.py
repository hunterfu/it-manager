#!/usr/bin/env python
# -*- coding: utf-8 -*-
import stock
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
#data = stock.get_historical_prices('ras','20100112','20110112')
#for item in data:
#	s_date = item[0]
#	s_open = item[1]
#	s_high = item[2]
#	s_low = item[3]
#	s_close = item[4]
#	s_volume = item[5]
#	print 'date = %s close = %s vol =%s' % (s_date,s_close,s_volume)

def analyse_stock(cache_file,symbol,stock_name,is_update=False):
    """
    分析
    """
    if os.path.isfile(cache_file):
        if is_update:
            all_data = stock.get_all(symbol)
            if not all_data: return "pass"
            # 持久化dict,用来cache文章修改时间
            fout = open(cache_file, "w")
            pickle.dump(all_data, fout, protocol=0)
            fout.close()
        else:
            fin = open(cache_file, "r")
            all_data  = pickle.load(fin)
            fin.close()
    else:
        time.sleep(2)
        all_data = stock.get_all(symbol)
        if not all_data: return "pass" 
        # 持久化dict,用来cache文章修改时间
        fout = open(cache_file, "w")
        pickle.dump(all_data, fout, protocol=0)
        fout.close()

    stock_exchange = all_data['stock_exchange']
    stock_exchange.strip()
    # 数据有误，需要删除
    regex=ur"N/A" #正则表达式
    if re.search(regex, stock_exchange): 
        return "del"

    p50day_moving_avg = all_data['50day_moving_avg']
    p200day_moving_avg = all_data['200day_moving_avg']
    price = all_data['price']
    avg_daily_volume = all_data['avg_daily_volume']
    volume = all_data['volume']
    earnings_per_share = all_data['earnings_per_share']
    dividend_yield = all_data['dividend_yield'] # 股息收益率
    pe = all_data['price_earnings_ratio'] # 市盈率
    is_vol = False          #交易量超过日平均交易量 
    is_over_200_5_percent = False    #当前价格在200天均线值的 +5% 之内
    is_over_200 = False    #当前价格在200天上
    is_between_50_200 = False   # 当前价格在50天均线和200天均线之间
    is_eps_over_bond = False    # 收益率大于债券收益率
    is_many_buyer = False       # 多头，看多
    output_str = None
    is_over_dividend_yield = False
    try:
        #价格低于 1.5,忽略 ||  平均成交量小于10万，忽略
        if float(price) < 1.5 or int(avg_daily_volume) < 100000:  return stock_exchange 
        # 上市不到一年的 忽略
        #if p200day_moving_avg == "0.00": return stock_exchange
        if pe == "0.00": return stock_exchange

        if (float(volume)/float(avg_daily_volume)) >=1.2:  is_vol = True
        if float(p200day_moving_avg) <= float(price) <= float(p200day_moving_avg) * 1.05 : is_over_200_5_percent = True 
        if float(p200day_moving_avg) <= float(price) : is_over_200 = True 
        #if float(p200day_moving_avg) * 0.95 <= float(price) <= float(p200day_moving_avg): print " 当前价格在200天均线值的 -5% 之内",
        if float(p50day_moving_avg) <= float(price) <= float(p200day_moving_avg) : is_between_50_200 = True
        #if float(p200day_moving_avg) <= float(price) <= float(p50day_moving_avg) : is_between_50_200 = True
        if float(p200day_moving_avg) <= float(p50day_moving_avg) <= float(price) : is_many_buyer = True
        if float(earnings_per_share) / 0.06 >= float(price): is_eps_over_bond = True
        if dividend_yield != "N/A" and float(dividend_yield) >= 10: is_over_dividend_yield =True

        over_200 = ""
        vol_up = ""
        between_50_200 = ""
        high_yield = ""
        if is_over_200_5_percent: over_200 = "200天均线上 + %5 "
        elif is_over_200: over_200 = "200天均线上"
        if is_vol: vol_up = "成交量放大1.2倍 "
        if is_between_50_200: between_50_200 = "价格介于50天均线和200天均线之间 " 
        #elif is_vol and is_over_200 and is_many_buyer:
        #    output_str = "候选股，可能是看多线上 参考"
        if is_over_dividend_yield: high_yield = " 高股息收益率"
        if is_eps_over_bond:
            index_1[symbol] = Decimal(pe)
            index_2[symbol] = Decimal(earnings_per_share) / Decimal(price)
            index_3[symbol] = "%s%s%s%s" % (over_200, vol_up , between_50_200 , high_yield)

        #if output_str: print "%s - %s Price:%s EPS:%s PE:%s" % (stock_exchange,symbol,price,earnings_per_share,pe)
        #if output_str: print "%s - %s(%s) Price:%s EPS:%s PE:%s = %s" % (stock_exchange,stock_name,symbol,price,earnings_per_share,pe,output_str)
        #if output_str: print "%s - %s(%s) = %s" % (stock_exchange,stock_name,symbol,output_str)
        return stock_exchange
    except Exception,e:
        print "%s(%s) ERROR = %s" % (stock_name,symbol,e)
        return stock_exchange

#cx = ""
def connect_db(db_file):
    """
    连接数据库
    """
    if os.path.isfile(db_file):
        cx = sqlite.connect(db_file)
        cu = cx.cursor()
        return (cu,cx,"old")
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


# 定义变量 
base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
cache_dir = "%s/cache" % (base_dir)
#symbol = "RAS"
#symbol = "AGNC"
symbol =""
try:
    symbol = sys.argv[1]
except Exception,e: 
    symbol = "RAS"

db_file = "%s/%s" % (cache_dir,symbol)


(db_cursor,cx,tag) = connect_db(db_file)
cx.text_factory=str

# 新建数据库
if tag =="new":
    current_time = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    one_year_ago = (datetime.datetime.now() - datetime.timedelta(days=730)).strftime("%Y%m%d")
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
    current_time = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    last_update_time = datetime.datetime.strptime(max_date,"%Y-%m-%d")
    want_update_time = (last_update_time + datetime.timedelta(days=1)).strftime("%Y%m%d")
    #want_update_time = last_update_time.strftime("%Y%m%d")
    if want_update_time <= current_time:
        data = stock.get_historical_prices(symbol,want_update_time,current_time)
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

# 分析股票 横盘时间(股价 +- 10%),正负叠加应该接近于0 才能说明是横盘
sql_cmd = "select s_date,s_close,s_volume from stock order by s_date DESC limit 260"
db_cursor.execute(sql_cmd)
rs = db_cursor.fetchall()
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

    #if (-10 <= change <= 10) and (-5 <= change_sum <= 5):
    #if -50 <= change_sum <= 2:
    # 价格在一定周期的均线价格 +- 5% 浮动
    if last_trade_price * Decimal(str("0.92")) <= Decimal(s_close) <= last_trade_price * Decimal(str("1.07")):
    #if last_trade_price * Decimal(str("0.98")) <= Decimal(s_close):
        #print "%s = %s = %s = %s" % (s_date,s_close,s_volume,change)
        result_list.append((s_date,s_close,s_volume,change))
        day_count = day_count + 1;
        volume_sum = volume_sum + s_volume
        price_sum = Decimal(s_close) + price_sum 
        change_sum = change_sum + change
        #last_trade_price = Decimal(price_sum / day_count)
        #print "DEBUG last_trade_price = %s" % last_trade_price
    else:
        if day_count != 0:
            avg_volume = volume_sum / day_count
            avg_price = Decimal(str(round(price_sum / day_count,3)))
        break

# 输出结果
#for index in range(len(result_list)):
#    (s_date,s_close,s_volume,change) = result_list[index]
#    print "%s = %s = %s = %s avg_volume = %s avg_price = %s change_sum = %s" % (s_date,s_close,s_volume,change,avg_volume,avg_price,change_sum)
h_day_count = len(result_list)
(s_date,s_close,s_volume,change) = result_list[0] # 取得最近一个交易日的数据
volume_increase_time = Decimal(str(round(Decimal(s_volume) / avg_volume,2)))
#output = "volume_increase_time = %s avg_price= %s change_sum= %s h_day= %s" % (volume_increase_time,avg_price,change_sum,h_day_count)
output = "%s,%s,%s,%s" % (volume_increase_time,avg_price,change_sum,h_day_count)

if change_sum >=0 and Decimal(s_volume) > avg_volume and Decimal(s_close) > avg_price:
    print "%s,处于横盘状态缓慢上涨中" % output
elif Decimal(s_volume) > avg_volume and Decimal(s_close) > avg_price:
    print "%s,处于横盘状态可能启动中" % output
else:
    print "%s,处于横盘状态待观察中" % output
