#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = 0.1

from lib import stock,TaLib
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
import datetime
import string
import pprint
import commands

def TA_pad_zeros(argvs):
    """
    技术分析格式化输出
    """
    end = argvs[1]
    try:
         seq = argvs[2]
    except:
         seq = [0,0]
    end = int(end)
    nseq = []
    for x in range(end):
         nseq.append(0)
    for x in seq:
         nseq.append(float(fpformat.fix(x,3)))
         #nseq.append(x)
    return nseq

def ta_rsi(symbol,base_dir,TimePeriod):
    """
    /*
    * TA_RSI - Relative Strength Index
    *
    * Input  = double
    * Output = double
    *
    * Optional Parameters
    * -------------------
    * optInTimePeriod:(From 2 to 100000)
    *    Number of period
    *
    *
    */
    """
    data = []
    rs = get_trade_data(symbol,base_dir,90)
    sorted_rs = sorted(rs, key=lambda result: result[0],reverse=False)
    for item in sorted_rs:
        (s_date,s_close,s_volume)  = item
        data.append(float(s_close))

    rsi_data = TA_pad_zeros(TaLib.TA_RSI(0,len(data)-1,data,TimePeriod))
    print rsi_data
    #return rsi_data 

def ta_macd(symbol,base_dir,FastPeriod=10,SlowPeriod=26,SignalPeriod=9):
    """
    /*
    * TA_MACD - Moving Average Convergence/Divergence
    *
    * Input  = double
    * Output = double, double, double
    *
    * Optional Parameters
    * -------------------
    * optInFastPeriod:(From 2 to 100000)
    *    Number of period for the fast MA
    *
    * optInSlowPeriod:(From 2 to 100000)
    *    Number of period for the slow MA
    *
    * optInSignalPeriod:(From 1 to 100000)
    *    Smoothing for the signal line (nb of period)
    *
    *
    */
    """
    data = []
    rs = get_trade_data(symbol,base_dir,120)
    sorted_rs = sorted(rs, key=lambda result: result[0],reverse=False)
    for item in sorted_rs:
        (s_date,s_close,s_volume)  = item
        data.append(float(s_close))

    macd_data = TaLib.TA_MACD(0,len(data)-1,data,FastPeriod,SlowPeriod,SignalPeriod)
    print len(macd_data[2])
    pprint.pprint(macd_data[2])
    #macd_data = TA_pad_zeros(TaLib.TA_MACD(0,len(data)-1,data,FastPeriod,SlowPeriod,SignalPeriod))
    #print macd_data

def ta_ma(symbol,base_dir,TimePeriod=50):
    """
    /*
     * TA_MA - Moving average
     *
     * Input  = double
     * Output = double
     *
     * Optional Parameters
     * -------------------
     * optInTimePeriod:(From 1 to 100000)
     *    Number of period
     *
     * optInMAType:
     *    Type of Moving Average
     *
     *
     */
    """
    data = []
    rs = get_trade_data(symbol,base_dir,90)
    sorted_rs = sorted(rs, key=lambda result: result[0],reverse=False)
    for item in sorted_rs:
        (s_date,s_close,s_volume)  = item
        data.append(float(s_close))
    ma_data = TA_pad_zeros(TaLib.TA_MA(0,len(data)-1,data,TimePeriod))
    print ma_data

def export_data(base_dir,symbol):
    """ 导出数据 """
    cache_dir = "%s/trade_db" % (base_dir)
    symbol = symbol.upper()
    db_file = "%s/%s" % (cache_dir,symbol)
    export_file = "/home/hua.fu/geniustrader/data/%s" % symbol.lower()
    cmd = "sqlite3 %s 'select s_date,s_open,s_high,s_low,s_close,s_volume from stock order by s_date' |sed -e 's/|/\\t/g' >%s.txt" % (db_file,export_file)
    (status,output) = commands.getstatusoutput(cmd)
    if status != 0: 
        print "======== Error ========="
        print output

    

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

def get_avg_price(symbol,base_dir,day=200):
    """ 得到50天或者200天均线价格"""
    (db_cursor,cx) = update_trade_data(symbol,base_dir)
    rs = None
    sql_cmd = "select s_close from stock stock order by s_date desc limit %s" % (day)
    db_cursor.execute(sql_cmd)
    rs = db_cursor.fetchall()
    cx.close()
    result = []
    for item in rs:
        result.append(float(item[0]))

    avg_price = sum(result) / day
    return avg_price

def get_avg_volume(symbol,base_dir,day=30):
    """ 得到30天平均交易量"""
    (db_cursor,cx) = update_trade_data(symbol,base_dir)
    rs = None
    sql_cmd = "select s_volume from stock stock order by s_date desc limit %s" % (day)
    db_cursor.execute(sql_cmd)
    rs = db_cursor.fetchall()
    cx.close()
    result = []
    for item in rs:
        result.append(item[0])

    avg_volume = sum(result) / day
    return avg_volume

def connect_db(db_file):
    """
    connect db
    channel 通道相关,上升通道或者下降通道,3个点 就可以确定通道方向
    fluctuation 价格波动区间，一般来说是横盘状态
    line 阻力线或者支撑线
    """
    if os.path.isfile(db_file):
        cx = sqlite.connect(db_file)
        cu = cx.cursor()
        return (cu,cx)
    else:
        #create
        #data field : 交易所,代码,股息收益率,净资产价格比率,现金价格比率,资产负债率,收益率,投资回报率,综合排名
        #exchange,symbol,dps_yield,stock_bps_yield,cash_yield,debt2asset,stock_earning_yield,stock_roi_ttm,top_order

        cx = sqlite.connect(db_file)
        cu = cx.cursor()
        cu.execute('''
            create table stock(
            id integer primary key,
            exchange_name varchar(20),
            stock_title varchar(50),
            stock_symbol varchar(20) UNIQUE,
            stock_last_price NUMERIC,
            channel_date_1 varchar(50),
            channel_date_2 varchar(50),
            channel_date_3 varchar(50),
            line_support NUMERIC,
            line_resistance NUMERIC,
            stock_trend varchar(100),
            stock_bottom_shape varchar(100),
            stock_top_shape varchar(100),
            stock_tradedb_lastupdate_time NUMERIC,
            stock_note varchar(1000),
            sma_50 NUMERIC DEFAULT 0,
            sma_200 NUMERIC DEFAULT 0,
            country varchar(100),
            avg_volume NUMERIC
            )''')
        return (cu,cx)


def update_db(db_cursor,cx,monitor_data):
    """ update db from monitor data(data filted by filter_stock prog """
    fin = open(monitor_data, "r")
    stock_list  = pickle.load(fin)
    fin.close()
    for item in stock_list:
        exchange = item[0]
        symbol = item[1]
        symbol = symbol.upper()
        # 判断是否已经插入数据库中
        sql_cmd = "select count(*) from stock where stock_symbol = '%s'" % (symbol)
        db_cursor.execute(sql_cmd)
        rs = db_cursor.fetchone()
        rs_count = rs[0]
        if not rs_count:
            sql_cmd = 'insert into stock (id,exchange_name,stock_symbol,stock_tradedb_lastupdate_time) values(NULL,"%s","%s",0)' % (exchange,symbol)
            db_cursor.execute(sql_cmd)
            cx.commit()

def update_channel(db_cursor,cx,stock_symbol,date_1,date_2,date_3):
    """ 设置通道数据    date_1,date_2,date_3 三个点为日期,根据日期自动计算 """
    sql_cmd = "update stock set channel_date_1='%s',channel_date_2='%s',channel_date_3='%s' where stock_symbol = '%s'" %(date_1,date_2,date_1,stock_symbol)
    db_cursor.execute(sql_cmd)
    cx.commit()
    print "Setting %s Channel data success" % (stock_symbol.upper())

def update_fluctuation(db_cursor,cx,stock_id,high_price,low_price,avg_price,peroid):
    """(横盘)设置波动数据   3个价格(最低，最高，平均价格),持续时间或者周期"""
    sql_cmd = 'update stock set fluctuation_price_high=%s,fluctuation_price_low=%s,fluctuation_price_avg=%s,fluctuation_period=%s where id = %s' %(high_price,low_price,avg_price,peroid,stock_id)
    db_cursor.execute(sql_cmd)
    cx.commit()
    
def update_line(db_cursor,cx,stock_symbol,s_line,r_line):
    """设置支撑线和阻力线 support_line,resistance_line"""
    sql_cmd = "update stock set line_support=%s,line_resistance=%s where stock_symbol = '%s'" %(s_line,r_line,stock_symbol)
    db_cursor.execute(sql_cmd)
    cx.commit()
    print "Setting %s line data success" % (stock_symbol.upper())

def delete_stock(db_cursor,cx,stock_symbol):
    """根据stock_symbol 删除"""
    sql_cmd = "delete from stock where stock_symbol = '%s'" %(stock_symbol)
    db_cursor.execute(sql_cmd)
    cx.commit()
    print "Delete %s success" % (stock_symbol.upper())

def analyse_avg_cost(base_dir,stock_symbol):
    #day_count = [5,10,20,30,60,120,200]
    day_count = range(0,50,5)
    del day_count[0]
    last_avg_cost_price = 0
    avg_tradevolume_dict = {}
    avg_tradeprice_dict = {}
    return_str = ""
    day = 0
    s_list = []
    for day in day_count:
        (s_avg_price,s_avg_trade_volume) = calculate_cost(base_dir,stock_symbol,day)
        if s_avg_price == 0: return (stock_symbol,0,0,"None")
        avg_tradevolume_dict[day]=s_avg_trade_volume
        avg_tradeprice_dict[day]=s_avg_price
        if last_avg_cost_price == 0: 
            last_avg_cost_price = s_avg_price
            s_list.append((day,s_avg_price,s_avg_trade_volume))
            continue
        # 平均成本价格在一定周期 +- 3% 浮动
        if last_avg_cost_price * Decimal(str("0.95")) <= Decimal(s_avg_price) <= last_avg_cost_price * Decimal(str("1.05")):
            s_list.append((day,s_avg_price,s_avg_trade_volume))
            continue
        else:
            break
    
    # 计算是否可能上涨 
    if len(s_list) >=2:
        day = s_list[len(s_list) -1][0]
        #avg_cost_price = avg_tradeprice_dict[day]
        stock_trend = "None"
        week_num = day / 5
        if avg_tradeprice_dict[10] <= avg_tradeprice_dict[5] and avg_tradevolume_dict[10] <= avg_tradevolume_dict[5]:
            #return_str =  "Symbol = %s : %s Week,AvgCostPrice = %.6s,%s" % (stock_symbol,week_num,avg_tradeprice_dict[day],"Uptrend")
            stock_trend = "Uptrend"
        elif avg_tradeprice_dict[5] <= avg_tradeprice_dict[10] and avg_tradevolume_dict[10] <= avg_tradevolume_dict[5]:
            #return_str =  "Symbol = %s : %s Week,AvgCostPrice = %.6s,%s" % (stock_symbol,week_num,avg_tradeprice_dict[day],"Downtrend")
            stock_trend = "Downtrend"
        elif avg_tradeprice_dict[5] <= avg_tradeprice_dict[10] and avg_tradevolume_dict[5] <= avg_tradevolume_dict[10]:
            #return_str =  "Symbol = %s : %s Week,AvgCostPrice = %.6s,%s" % (stock_symbol,week_num,avg_tradeprice_dict[day],"Attention")
            stock_trend = "Attention"
        elif avg_tradeprice_dict[10] <= avg_tradeprice_dict[5] and avg_tradevolume_dict[5] <= avg_tradevolume_dict[10]:
            #return_str =  "Symbol = %s : %s Week,AvgCostPrice = %.6s,%s" % (stock_symbol,week_num,avg_tradeprice_dict[day],"CloseToTop")
            stock_trend = "CloseToTop"
        # 计算平均成本
        sum_trade_money = 0
        sum_trade_volume = 0
        avg_trade_volume = 0
        for item in s_list:
            (s_date,s_avg_price,s_avg_volume)  = item
            sum_trade_money = Decimal(s_avg_price) * s_avg_volume + sum_trade_money
            sum_trade_volume = sum_trade_volume + s_avg_volume

        avg_cost_price = sum_trade_money / sum_trade_volume
        return (stock_symbol,week_num,avg_cost_price,stock_trend)
    else:
        return (stock_symbol,1,last_avg_cost_price,"None")
    #else:
    #    return_str =  "Symbol = %s : %s Week,AvgCostPrice = %.6s" % (stock_symbol,week_num,avg_tradeprice_dict[day])
    #return return_str
def print_stock(db_cursor,cx,stock_region):
    """ 
    打印符合条件的股票 
    """
    sql =""
    #condiction_sql = "(stock_last_price >= sma_50 and stock_last_price <= sma_200) or (stock_last_price >= sma_200 and stock_last_price <= sma_50)"
    #condiction_sql = "(stock_last_price >= sma_200 and stock_last_price <= sma_50)"
    time_now = int(time.time())
    #condiction_sql = "(stock_last_price >= sma_50 and stock_last_price <= sma_200) and stock_tradedb_lastupdate_time <= %s" % (time_now)
    #condiction_sql = "(stock_last_price >= sma_200 and stock_last_price <= sma_50) and stock_tradedb_lastupdate_time <= %s" % (time_now)
    #condiction_sql = "stock_last_price >= sma_200 and stock_tradedb_lastupdate_time <= %s" % (time_now)
    #condiction_sql = "stock_last_price >=sma_200 and stock_last_price <= sma_200*1.05 and stock_tradedb_lastupdate_time <= %s" % (time_now)
    #condiction_sql = "stock_last_price >=sma_50 and stock_last_price <= sma_200*1.05 and stock_tradedb_lastupdate_time <= %s" % (time_now)
    #condiction_sql = "stock_trend = 'Uptrend' and stock_bottom_shape='DoubleBottom' and stock_tradedb_lastupdate_time <= %s" % (time_now)
    #condiction_sql = "(stock_last_price >=sma_50 and stock_last_price <= sma_200*1.05) or stock_last_price >sma_200 and stock_bottom_shape='DoubleBottom' and stock_tradedb_lastupdate_time <= %s" % (time_now)
    # 买多 
    #condiction_sql = "(stock_last_price >=sma_50 and stock_last_price <= sma_200)  and stock_bottom_shape='DoubleBottom' and stock_tradedb_lastupdate_time <= %s" % (time_now)
    condiction_sql = "(stock_last_price >=sma_50 and stock_last_price <= sma_200)  and stock_tradedb_lastupdate_time <= %s" % (time_now)
    #condiction_sql = "stock_last_price >= sma_50 and stock_last_price <= sma_200*1.03  and stock_bottom_shape='DoubleBottom' and stock_tradedb_lastupdate_time <= %s" % (time_now)
    # 卖空
    #condiction_sql = "stock_last_price < sma_200 and stock_top_shape='DoubleTop' and stock_tradedb_lastupdate_time <= %s" % (time_now)
    if stock_region:
        stock_region=stock_region.upper()
        sql = "select * from stock where country = '%s' and (%s) order by stock_symbol" % (stock_region,condiction_sql)
    else:
        sql = "select * from stock where %s order by stock_symbol" % (condiction_sql)
    db_cursor.execute(sql)
    rs = db_cursor.fetchall()
    # print title
    if len(rs) == 0 : return
    #print "代码\t名称\t最新价格\t趋势\t底形态\t顶形态\tOver_50SMA\tOver_200SMA"
    print "代码\t名称\t最新价格\t趋势\t底形态\t顶形态"
    for item in rs:
        title = item[2]
        symbol = item[3]
        last_price = item[4] 
        trend = item[10]
        bottom_shape = item[11]
        stock_top_shape = item[12] 
        SMA50 = item[15] 
        SMA200 = item[16] 
        over_50 = "False"
        over_200 = "False"
        if last_price > SMA50 : over_50 = "True" 
        if last_price > SMA200 : over_200 = "True"
        #print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (symbol,title,last_price,trend,bottom_shape,stock_top_shape,over_50,over_200)
        print "%s\t%s\t%s\t%s\t%s\t%s" % (symbol,title,last_price,trend,bottom_shape,stock_top_shape)

def analyse_stock(db_cursor,cx,base_dir,symbol=None,title=None,stock_region='US'):
    """ 
    自动分析 横盘状态,支撑线和阻力线 
    """
    sql = ""
    if symbol:
        sql = "select * from stock where stock_symbol='%s'" % symbol
    else:
        time_now = int(time.time())
        last_update_time = time_now - 43200
        stock_region = stock_region.upper()
        #last_update_time = time_now - 600
        sql = "select * from stock where stock_tradedb_lastupdate_time <= %s and country = '%s'" % (last_update_time,stock_region)
    db_cursor.execute(sql)
    rs = db_cursor.fetchall()
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
        return
    elif len(rs)>0:
        #(stock_symbol,week_num,avg_cost_price,stock_trend) = analyse_avg_cost(db_cursor,cx,base_dir,symbol)
        #(last_close_price,last_date) = analyse_henpan(base_dir = base_dir,symbol = symbol)
        #(low_shape,top_shape) = estimate_stock_shape(symbol = symbol,base_dir = base_dir,day_count=60)
        #print "%s\t%s\t%s\t%.6s\t%s\t%s\t%s" % (stock_symbol,last_close_price,week_num,avg_cost_price,stock_trend,low_shape,top_shape)
        
        print "代码\t最新价格\t持续周\t平均价格\t趋势\t底形态\t顶形态"
        for item in rs:
            stock_id = item[0]
            exchange = item[1]
            symbol = item[3]
            if symbol.find("/") != -1 or symbol.find("^") != -1:
                delete_stock(db_cursor,cx,symbol)
                #print "delete symbol = %s" % (symbol)
                continue
            last_price = item[4] or 0
            trend = item[10] or None
            bottom_shape = item[11] or None
            stock_top_shape = item[12] or None
            stock_tradedb_lastupdate_time = item[13] or 0
            stock_avg_volume = item[18] or 0
            global tradedb_lastupdate_time
            tradedb_lastupdate_time = stock_tradedb_lastupdate_time
            # 分析横盘结果
            if DEBUG: print "DEBUG SYMBOL = %s" % symbol
            smbol = symbol.upper()
            export_data(base_dir,symbol)
            try:
                (stock_symbol,week_num,avg_cost_price,stock_trend) = analyse_avg_cost(base_dir,symbol)
                (last_close_price,last_date) = analyse_henpan(base_dir = base_dir,symbol = symbol)
                avg_volume = get_avg_volume(symbol,base_dir,30)
                if float(last_close_price) <= 0.5:
                    delete_stock(db_cursor,cx,symbol)
                    continue
                if float(last_close_price) <=1.5: 
                    # 一个月后再检查
                    next_check_time = int(time.time()) + 2592000
                    sql_cmd = "update stock set stock_tradedb_lastupdate_time = %s where stock_symbol='%s'" % (next_check_time,symbol)
                    db_cursor.execute(sql_cmd)
                    cx.commit()
                    continue
                if  avg_volume < 200000: 
                    # 2周后检查
                    next_check_time = int(time.time()) + 604800
                    sql_cmd = "update stock set stock_tradedb_lastupdate_time = %s where stock_symbol='%s'" % (next_check_time,symbol)
                    db_cursor.execute(sql_cmd)
                    cx.commit()
                    continue
                (low_shape,top_shape) = estimate_stock_shape(symbol = symbol,base_dir = base_dir,day_count=60)
                sma_50 = get_avg_price(symbol,base_dir,50)
                sma_200 = get_avg_price(symbol,base_dir,200)
                #print "------ Sma50 = %s Sma200 = %s ---------" % (sma_50,sma_200)
                #if last_close_price > sma_50 or last_close_price > sma_200:
                print "%s\t%s\t%s\t%.6s\t%s\t%s\t%s" % (stock_symbol,last_close_price,week_num,avg_cost_price,stock_trend,low_shape,top_shape)
                sql_cmd = None
                update_list = []
                if last_price != float(last_close_price):
                    sql_cmd = "stock_last_price = %s" % last_close_price 
                    update_list.append(sql_cmd)
                if title:
                    sql_cmd = "stock_title='%s'" % (title)
                    update_list.append(sql_cmd)
                if stock_trend != trend:
                    sql_cmd = "stock_trend='%s'" % (stock_trend)
                    update_list.append(sql_cmd)
                if bottom_shape != low_shape:
                    sql_cmd = "stock_bottom_shape='%s'" % (low_shape)
                    update_list.append(sql_cmd)
                if stock_top_shape != top_shape:
                    sql_cmd = "stock_top_shape='%s'" % (top_shape)
                    update_list.append(sql_cmd)
                if stock_avg_volume != avg_volume:
                    sql_cmd = "avg_volume='%s'" % (avg_volume)
                    update_list.append(sql_cmd)
                #if tradedb_lastupdate_time != stock_tradedb_lastupdate_time:
                time_now = int(time.time())
                sql_cmd = "stock_tradedb_lastupdate_time = %s" % (time_now)
                update_list.append(sql_cmd)
                sql_cmd = "sma_50 = %s" % sma_50
                update_list.append(sql_cmd)
                sql_cmd = "sma_200 = %s" % sma_200
                update_list.append(sql_cmd)

                if len(update_list)>0:
                    update = ",".join(update_list)
                    sql_cmd = "update stock set %s where stock_symbol='%s'" % (update,symbol)
                    #print "sql_cmd = %s" % sql_cmd
                    db_cursor.execute(sql_cmd)
                    cx.commit()
            #except Exception,e:
            except (InvalidOperation,DivisionByZero),e:
                print "%s === Error = %s " % (symbol,e)
                #delete_stock(db_cursor,cx,symbol)
            except IOError,e:
                print "%s === Error = %s"  % (symbol,e)
                #time_now = int(time.time())
                #delete_stock(db_cursor,cx,symbol)
                #sql_cmd = "update stock set stock_tradedb_lastupdate_time = %s where stock_symbol='%s'" % (time_now,symbol)
                #db_cursor.execute(sql_cmd)
                #cx.commit()


def estimate_stock_shape(symbol,base_dir,day_count=30):
    """
    估算股票形态
    """
    low_point = get_low_point(symbol,base_dir) 
    top_point = get_top_point(symbol,base_dir)
    return (low_point,top_point)

def get_low_point(symbol,base_dir):
    """ 得到给定时间的支撑点 """
    day = 10
    last_len = 0
    rs = get_trade_data(symbol,base_dir,day)
    if len(rs) == 0:
        print "Symbol = %s : ==== No record,please check ====" % (symbol)
        return None
    # 价格差在0.5%元之间
    sorted_list = sorted(rs, key=lambda result: Decimal(result[1]),reverse=False)
    #print sorted_list
    #continue
    last_trade_price = 0
    s_list = []
    low_val_len = 0
    for item in sorted_list:
        #low_1 = sorted_list[0][1]
        #low_2 = sorted_list[1][1]
        #low_1 = item[1]
        if last_trade_price == 0: 
            last_trade_price = item[1]
            s_list.append(item)
            continue
        low_2 = item[1]
        if (Decimal(low_2) - Decimal(last_trade_price)) / Decimal(last_trade_price) <= 0.005:
            s_list.append(item)
        else:
            break
    return get_double_bottom(symbol,base_dir,s_list)

def get_double_bottom(symbol,base_dir,low_list):
    """
     计算双底
    """
    if len(low_list) >= 2:
        s_date = sorted(low_list, key=lambda result: result[0],reverse=False)
        start_date = s_date[0][0]
        end_date = s_date[len(low_list)-1][0]
        low_1 = s_date[0][1]
        low_2 = s_date[len(low_list)-1][1]
        low_1_volume = s_date[0][2]
        low_2_volume = s_date[len(low_list)-1][2]
        rs = get_trade_data_by_date(symbol,base_dir,start_date,end_date)
        if len(rs) >= 1:
            sorted_list = sorted(rs, key=lambda result: Decimal(result[1]),reverse=True)
            top_1 = sorted_list[0][1]
            if Decimal(top_1) > Decimal(low_1) and Decimal(top_1) > Decimal(low_2) and low_1_volume > low_2_volume:
                return "DoubleBottom"
    return "None"            

def get_top_point(symbol,base_dir):
    """ 得到给定时间的阻力点 """
    day = 10
    rs = get_trade_data(symbol,base_dir,day)
    if len(rs) == 0:
        print "Symbol = %s : ==== No record,please check ====" % (symbol)
        return "None"
    # 价格差在0.5%元之间
    sorted_list = sorted(rs, key=lambda result: Decimal(result[1]),reverse=True)
    last_trade_price = 0
    s_list = []
    for item in sorted_list:
        if last_trade_price == 0:
            last_trade_price = item[1]
            s_list.append(item)
            continue
        top_2 = item[1]
        if (Decimal(last_trade_price) - Decimal(top_2)) / Decimal(last_trade_price) <= 0.005:
            s_list.append(item)
        else:
            break
    return get_double_top(symbol,base_dir,s_list)


def get_double_top(symbol,base_dir,top_list):
    """
     计算双顶
    """
    if len(top_list) >= 2:
        s_date = sorted(top_list, key=lambda result: result[0],reverse=False)
        start_date = s_date[0][0]
        end_date = s_date[len(top_list)-1][0]
        top_1 = s_date[0][1]
        top_2 = s_date[len(top_list)-1][1]
        top_1_volume = s_date[0][2]
        top_2_volume = s_date[len(top_list)-1][2]
        rs = get_trade_data_by_date(symbol,base_dir,start_date,end_date)
        if len(rs) >= 1:
            sorted_list = sorted(rs, key=lambda result: Decimal(result[1]),reverse=False)
            low1 = sorted_list[0][1]
            if Decimal(top_1) > Decimal(low1) and Decimal(top_2) > Decimal(low1) and top_1_volume > top_2_volume:
                return "DoubleTop"
    return "None"            

def calculate_cost(base_dir,symbol,day_count=30):
    """ 
    估算持仓成本价格
    """
    #rs = get_trade_data(symbol,base_dir,day_count)
    offset = day_count - 5
    rs = get_trade_data(symbol,base_dir,day_count,offset)
    if len(rs) == 0:
        print "Symbol = %s : ==== No record,please check ====" % (symbol)
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
        avg_trade_volume = sum_trade_volume / day_count
    if DEBUG:
        print "=== %3s Week ,AvgCostPrice = %.8s ,AvgTradeVolume = %s" % (day_count/5,avg_cost_price,convert_number_to_money(avg_trade_volume))
    return (avg_cost_price,avg_trade_volume)
        
            
def connect_trade_db(db_file):
    """
    连接历史交易数据库
    """
    if os.path.isfile(db_file):
        #if int(time.time()) - int(os.stat(db_file).st_mtime) >= 43200:
        #time_now = int(time.time())
        #global tradedb_lastupdate_time
        #if time_now - tradedb_lastupdate_time >= 43200:
        #if time_now - tradedb_lastupdate_time >= 10:
        cx = sqlite.connect(db_file)
        cu = cx.cursor()
        #tradedb_lastupdate_time = time_now
        return (cu,cx,"old")
        #else:
        #    cx = sqlite.connect(db_file)
        #    cu = cx.cursor()
        #    return (cu,cx,"nothing")
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
    """ 更新历史交易数据库 """
    # 新建数据库
    if tag =="new":
        #current_time = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
        current_time = datetime.datetime.now().strftime("%Y%m%d")
        one_year_ago = (datetime.datetime.now() - datetime.timedelta(days=300)).strftime("%Y%m%d")
        data = stock.get_historical_prices(symbol,one_year_ago,current_time)
        if not data:
            return 
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
            #current_time = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
            current_time = datetime.datetime.now().strftime("%Y%m%d")
            last_update_time = datetime.datetime.strptime(max_date,"%Y-%m-%d")
            want_update_time = (last_update_time + datetime.timedelta(days=1)).strftime("%Y%m%d")
        else:
            #current_time = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
            current_time = datetime.datetime.now().strftime("%Y%m%d")
            want_update_time = (datetime.datetime.now() - datetime.timedelta(days=300)).strftime("%Y%m%d")
    
        #want_update_time = last_update_time.strftime("%Y%m%d")
        if datetime.datetime.now().weekday() in [0,6]: return  
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
                    s_volume = item[5]
                    if not s_volume.isdigit(): continue
                    sql_cmd = 'insert into stock values(NULL,"%s","%s","%s","%s","%s",%s)' % (s_date,s_open,s_high,s_low,s_close,s_volume)
                    #print "sql_cmd = " + sql_cmd
                    db_cursor.execute(sql_cmd)
                    cx.commit()

def update_trade_data(symbol,base_dir):
    """ 更新交易数据 """
    cache_dir = "%s/trade_db" % (base_dir)
    symbol = symbol.upper()
    db_file = "%s/%s" % (cache_dir,symbol)
    (db_cursor,cx,tag) = connect_trade_db(db_file)
    cx.text_factory=str
    update_trade_db(db_cursor,cx,symbol,tag)
    return (db_cursor,cx)
   
    
def get_trade_data(symbol,base_dir,days,offset=None):
    """ 得到固定天数的交易数据或者固定偏移天数数据"""
    (db_cursor,cx) = update_trade_data(symbol,base_dir)
    rs = None
    if offset:
        sql_cmd = "select s_date,s_close,s_volume from stock order by s_date DESC limit %s,5" % (offset)
        db_cursor.execute(sql_cmd)
        rs = db_cursor.fetchall()
        cx.close()
    else:
        sql_cmd = "select s_date,s_close,s_volume from stock order by s_date DESC limit %s" % days
        db_cursor.execute(sql_cmd)
        rs = db_cursor.fetchall()
        cx.close()
    return rs

def get_trade_data_by_date(symbol,base_dir,start_date,end_date):
    """ 得到固定日期之间的交易数据 """
    (db_cursor,cx) = update_trade_data(symbol,base_dir)
    sql_cmd = "select s_date,s_close,s_volume from stock  where s_date>'%s' and s_date < '%s'" % (start_date,end_date)
    db_cursor.execute(sql_cmd)
    rs = db_cursor.fetchall()
    cx.close()
    return rs

def analyse_henpan(base_dir,symbol='ras'):
    """ 分析横盘状态 """ 
    # 分析股票 横盘时间(股价 +- 10%),正负叠加应该接近于0 才能说明是横盘
    rs = get_trade_data(symbol,base_dir,260)
    l_date = []
    l_close = []
    l_volume = []
    if len(rs) == 0:
        return_str = "Symbol = %s,No record,please check" % (symbol)
        return (0,0)
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
        if day_count > 9:
            break
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
        #if last_trade_price * Decimal(str("0.97")) <= Decimal(s_close) <= last_trade_price * Decimal(str("1.03")):
        result_list.append((s_date,s_close,s_volume,change))
        day_count = day_count + 1;
        volume_sum = volume_sum + s_volume
        price_sum = Decimal(s_close) + price_sum 
        change_sum = change_sum + change
        #last_trade_price = Decimal(s_close)
        #else:
        # 横盘时间不能太短，小于3天无效
        #    break
           
    # 输出结果

    if day_count < 3: 
        #return_str = "Last_close_price = %s (Date : %s)" % (l_close[0],l_date[0])
        #return return_str
        return (l_close[0],l_date[0])
    
    if volume_sum == 0:
        print "ten day volume_sum is 0,delete this stock"
        return (0,0)
    avg_volume = volume_sum / day_count
    avg_price = Decimal(str(round(price_sum / day_count,3)))
    # 计算横盘数据的最高值和最小值
    sorted_data = sorted(result_list, key=lambda result: Decimal(result[1]),reverse=True)
    price_max = sorted_data[0][1]
    sorted_data = sorted(result_list, key=lambda result: Decimal(result[1]))
    price_min = sorted_data[0][1]

    
    # 调试输出    
    if DEBUG:
        print "Debug : ===========  Symbol : %s  =================================" % (symbol)
        for index in range(len(result_list)):
            (s_date,s_close,s_volume,change) = result_list[index]
            volume_increase_time = Decimal(str(round(Decimal(s_volume) / avg_volume,2)))
            print "%s = %s = volume_increase_time :%s = %s" % (s_date,s_close,volume_increase_time,change)       
        print "-------------- Max = %s , Min = %s --------------" % (price_max,price_min)
    #return (price_max,price_min,avg_price,day_count)   
    #return_str = "Last_close_price = %s (Date : %s)" % (l_close[0],l_date[0])
    #return return_str
    return (l_close[0],l_date[0])

    
def usage():
    print '''
Usage: monitor_stock.py [options...]
Options: 
    -e/--exchane                        : Exchange Name 
    -t/--title                          : Stock title
    -s/--symbol                         : Stock symbol
    -l/--Line <s_line,r_lie>            : setting support_line and resistance_line
    -c/--channel <date1,date2,date3>    : setting channel,three date point 
    -d/--debug                          : run in debug mode 
    -D/--delete                         : delete stock
    -p/--print                          : print stock 
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
    base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    cache_dir = "%s/tmp" % (base_dir)
    monitor_data = "%s/monitor_data" % (cache_dir)
    monitor_db = "%s/db/monitor_db" % (base_dir)
    # 判断 monitor_data 是否存在
    #if not os.path.isfile(monitor_data):
    #    print "%s not exists,please check!!!!" % monitor_data
    #    sys.exit(1)
        
    try:
        opts, args = getopt.getopt(sys.argv[1:],'pDdhe:t:s:l:c:r:')
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
    global DEBUG
    DEBUG = False
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
        elif opt == '-s':
            stock_code =  arg
        elif opt == '-l':
            stock_line = arg
        elif opt == '-c':
            stock_channel = arg
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

    #if os.path.isfile(monitor_db) and (int(time.time()) - int(os.stat(monitor_data).st_mtime) <= 86400) :
    #    #print "%s last check time due now less than 86400 seconds,ignore update db" % monitor_data
    #    (db_cursor,cx) = connect_db(monitor_db)
    #    cx.text_factory=str
    #else:
    #    #更新数据
    #    (db_cursor,cx) = connect_db(monitor_db)
    #    cx.text_factory=str
    #    update_db(db_cursor,cx,monitor_data)
    (db_cursor,cx) = connect_db(monitor_db)
    cx.text_factory=str

    if stock_symbol and stock_line:
        try:
            (line1,line2) = stock_line.split(",")
            s_line = min(line1,line2)   # 支撑线
            r_line = max(line1,line2)   # 阻力线
            #print "s_line=%s,r_line=%s" % (s_line,r_line)
            update_line(db_cursor,cx,stock_symbol,s_line,r_line)
        except Exception,e:
            print "setting line data format wrong,ErrMsg = %s" % (e)
            usage()
            sys.exit()
    elif stock_symbol and stock_channel:
        try:
            (date_1,date_2,date_3) = stock_channel.split(",")
            d1 = datetime.datetime.strptime(date_1,"%Y-%m-%d")
            d2 = datetime.datetime.strptime(date_2,"%Y-%m-%d")
            d3 = datetime.datetime.strptime(date_3,"%Y-%m-%d")
            #rint "d1=%s,d2=%s,d3=%s" % (date1,date2,date3)
            update_channel(db_cursor,cx,stock_symbol,date_1,date_2,date_3)
        except Exception,e:
            print "setting channel data format wrong,ErrMsg = %s" % (e)
            usage()
            sys.exit()
    elif stock_symbol and is_delete:
        try:
            delete_stock(db_cursor,cx,stock_symbol)
        except Exception,e:
            print "setting line data format wrong,ErrMsg = %s" % (e)
            usage()
            sys.exit()
    elif stock_symbol:
        analyse_stock(db_cursor,cx,base_dir,stock_symbol,stock_title)
        #estimate_stock_shape(stock_symbol,base_dir)
        #ta_rsi(stock_symbol,base_dir,6)
        #ta_macd(stock_symbol,base_dir)
        #ta_ma(stock_symbol,base_dir)
    elif is_print and stock_region:
        print_stock(db_cursor,cx,stock_region)
    elif stock_region:
        analyse_stock(db_cursor,cx,base_dir,stock_region=stock_region)
    else:
        analyse_stock(db_cursor,cx,base_dir)
    # 分析横盘结果    
    #print analyse_henpan(base_dir = base_dir,symbol = symbol)
    
    
    cx.close()    
if __name__ == "__main__":
    main()

