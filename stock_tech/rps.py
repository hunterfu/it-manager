#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = 0.1

from lib import stock
from lib.htmltmpl import TemplateManager, TemplateProcessor

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
import smtplib

"""
股票相对强弱指标(年，半年，季度，月，2周)
针对大盘指数涨跌幅对比
"""

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


def connect_pool_db(db_file):
    """
    筛选出的票池列表  
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
            symbol varchar(20) UNIQUE,
            top_order integer,
            country varchar(100),
            firstsee_time NUMERIC DEFAULT 0,
            lastupdate_time NUMERIC DEFAULT 0
            )''')
        return (cu,cx)


def calc_stock(stock_list,country):
    """ 
    计算rps
    """
    graph_dir = "/home/hua.fu/geniustrader/Scripts"
    result_data = []
    if len(stock_list) == 0 : return result_data
    # 标普500指数作为基准
    index_name = base_index[country][0]
    index_symbol = base_index[country][1]
    #base_list = get_rps('^GSPC')
    base_list = get_rps(index_symbol)
    #base_list = get_increase(base_list)

    #print "代码\t12周\t10周\t8周\t6周\t4周\t2周\t最新价格"
    stock_list.append(index_symbol)
    for symbol in stock_list:
        symbol = symbol.upper()
        if not symbol in ['000001.SS','^GSPC']:
            if not stock_filter(symbol): continue
        ret_list = get_rps(symbol)
        # 不符合筛选周期的
        if len(ret_list) == 0:
            continue

        # 数据有问题
        if len(ret_list) != 7:
            update_stock(symbol)
            continue

        # 以大盘为基准进行过滤
        is_condiction = False
        for i in range(len(ret_list)):
            if not ret_list[i] >= base_list[i]:
                break
            if i == 0 : 
                continue
            if base_list[i] >= base_list[i-1]:
                if not ret_list[i] >= ret_list[i-1]:
                    break
            if i+1 == len(ret_list):
                is_condiction= True

        if not is_condiction:
            continue

        # 过滤掉涨幅过大的比如超过15%
        #if ret_list[6] >= 16: continue

        #print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (symbol,ret_list[0],ret_list[1],ret_list[2],ret_list[3],ret_list[4],ret_list[5],ret_list[6])
        tmp_str = "%s,%s,%s,%s,%s,%s,%s,%s" % (symbol,ret_list[0],ret_list[1],ret_list[2],ret_list[3],ret_list[4],ret_list[5],ret_list[6])
        data = tuple(tmp_str.split(","))
        result_data.append(data)

    return result_data

def create_graph(stock_list,template_file,conf_dir,stock_region='US',signal_file="signal_file",endday='today'):
    """
    根据股票代码生成图片
    """
    out_dir = "/home/hua.fu/geniustrader/output"
    graph_conf = "%s/graph_day.conf" % (conf_dir)
    template_graph_conf = "/tmp/graph_%s.conf" % (signal_file)
    graph_week_conf = "%s/graph_week.conf" % (conf_dir)
    graph_month_conf = "%s/graph_month.conf" % (conf_dir)
    stock_count = len(stock_list)
    template = TemplateManager().prepare(template_file)
    tproc = TemplateProcessor(html_escape=0)
    stock = []
    for symbol in stock_list:
        symbol = symbol.strip()
        img_file = "%s/%s.png" % (out_dir,symbol)
        img_week_file = "%s/%s_WEEK.png" % (out_dir,symbol)
        img_month_file = "%s/%s_MONTH.png" % (out_dir,symbol)
        cmd = "cd /home/hua.fu/geniustrader/Scripts;./graphic.pl --end '%s' --file %s --out '%s' %s" % (endday,graph_conf,img_file,symbol)
        #print "DEBUG graph_cmd = %s" % cmd
        (status,output) = commands.getstatusoutput(cmd)
        cmd = "cd /home/hua.fu/geniustrader/Scripts;./graphic.pl --file %s --out '%s' %s" % (graph_week_conf,img_week_file,symbol)
        #print "DEBUG graph_cmd = %s" % cmd
        (status,output) = commands.getstatusoutput(cmd)
        if status != 0: 
            print "====== Error ======"
            print output
            continue
        stock_dict= {}
        stock_dict['symbol'] = symbol
        stock_dict['img'] = img_file
        stock_dict['img_week'] = img_week_file
        #stock_dict['img_month'] = img_month_file
        stock.append(stock_dict)

    #pprint.pprint(stock)
    tproc.set("market_name","%s Market" % stock_region)
    tproc.set("stock_count",stock_count)
    tproc.set("Stock",stock)
    # save to file
    filename = "%s/%s_%s_STOCK.html" % (out_dir,stock_region,signal_file)
    FILE = open(filename,"w")
    FILE.writelines(tproc.process(template))
    FILE.close()
 
def export_stock_symbol(db_cursor,cx):
    """ 
    导出股票代码名称对应列表 
    """
    sql = "select * from stock order by stock_symbol"
    #print "DEBUG sql = %s" % sql
    db_cursor.execute(sql)
    rs = db_cursor.fetchall()
    # print title
    if len(rs) == 0 : return
    sharenames = "/home/hua.fu/.gt/sharenames"
    os.system("rm -fr %s" % sharenames)
    share_FILE = open(sharenames,"w")

    for item in rs:
        title = item[2]
        symbol = item[3]
        country = item[4]
        if title:
            stock_map = symbol + "\t" + title
            share_FILE.writelines(stock_map + "\n")
        else:
            stock_map = symbol + "\t" + "No title"
            share_FILE.writelines(stock_map + "\n")
        
    share_FILE.close()


def get_stock_list(db_cursor,cx,stock_region='US'):
    """ 
    将符合条件的股票列表导出 
    """
    sql =""
    time_now = int(time.time())
    sql = "select * from stock where stock_tradedb_lastupdate_time <= %s and stock_country = '%s' order by stock_symbol" % (time_now,stock_region)
    #sql = "select * from stock where stock_tradedb_lastupdate_time <= %s and stock_country = '%s' ORDER BY RANDOM() limit 10" % (time_now,stock_region)
    db_cursor.execute(sql)
    rs = db_cursor.fetchall()
    if len(rs) == 0 : return
    stock_list = []
    for item in rs:
        symbol = item[3]
        stock_list.append(symbol)
    return stock_list


def get_rps(symbol):
    """
    1季度，2季度，3季度，4季度,月，2周
    or
    连续3个月和大盘强度对比
    """
    #peroid_offet = 5
    days = peroid_offet * 6
    symbol = symbol.upper()
    ret_list = []
    rs = get_trade_data(symbol,days);
    if len(rs) != days:
        return ret_list
    #period_list = [60,50,40,30,20,10,1]
    period_list = []
    day_list = range(1,days+1)
    day_list.reverse()
    for day in day_list:
        if day % peroid_offet == 0 :
            period_list.append(day)
      
    period_list.append(1)
    #print"normal peroid_list = %s "%  len(period_list)

    #period_list = [260,200,100,50,25,10,1]
    #rs = get_trade_data(symbol,260);
    #if len(rs) < 260:
    #    return ret_list
    #psrint"test peroid_list = %s "%  len(period_list)

    #last_price = rs[0][1]
    base_price = None
    #for i in test_list:
    #    try:
    #        base_price = rs[i-1][1]
    #        break;
    #    except Exception,e:
    #        period_list.remove(i)
    #        ret_list.append(0.0)
    #        continue 
    #for compare_day in [0,129,194,229,249]:
    #print "DEBUG period_lit =  symbol = %s" % symbol
    #print period_list
    for compare_day in period_list:
        #print "debug ==="
        #print rs[compare_day]
        try:
            compare_price = rs[compare_day - 1][1]
            if not base_price:
                base_price = compare_price
            change = (Decimal(compare_price) - Decimal(base_price))/Decimal(compare_price) * 100
            #change = (Decimal(compare_price) - Decimal(last_price))/Decimal(compare_price) * 100
            #change = (Decimal(last_price) - Decimal(compare_price))/Decimal(compare_price) * 100
            change = Decimal(str(round(change, 2)))
            ret_list.append(change)
        except Exception,e:
            #ret_list.append(0.0)
            return ret_list
    return ret_list

def get_increase(increse_list):
    """
    得到涨幅增长率
    """
    #last_price = rs[0][1]
    ret_list = []
    base_price = None
    #for i in test_list:
    #    try:
    #        base_price = rs[i-1][1]
    #        break;
    #    except Exception,e:
    #        period_list.remove(i)
    #        ret_list.append(0.0)
    #        continue 
    #for compare_day in [0,129,194,229,249]:
    #print "DEBUG period_lit =  symbol = %s" % symbol
    #print period_list
    for increase_price in increse_list:
        #print "debug ==="
        #print rs[compare_day]
        if increase_price == 0:
            ret_list.append(0.0)
            continue
        if not base_price:
            base_price = increase_price
        change = (Decimal(increase_price) - Decimal(base_price))/Decimal(base_price) * 100
        change = Decimal(str(round(change, 2)))
        base_price = increase_price
        ret_list.append(change)
    return ret_list
def get_trade_data(symbol,days=260):
    """ 得到固定天数的交易数据或者固定偏移天数数据"""
    (db_cursor,cx) = connect_trade_db(symbol)
    sql_cmd = "select s_date,s_close,s_volume from stock order by s_date DESC limit %s" % days
    db_cursor.execute(sql_cmd)
    rs = db_cursor.fetchall()
    cx.close()
    return rs

def connect_trade_db(symbol):
    """
    连接历史交易数据库
    """
    cache_dir = "%s/trade_db" % (base_dir)
    symbol = symbol.upper()
    db_file = "%s/%s" % (cache_dir,symbol)

    if os.path.isfile(db_file) and os.path.getsize(db_file) != 0:
        cx = sqlite.connect(db_file)
        cu = cx.cursor()
        cx.text_factory=str
        return (cu,cx)
    else:
        print "Symbol = %s ,Not find trade data,please check" % symbol
        return (False,False)

def stock_filter(symbol):
    """ filter stock data by condition """
    last_price = get_avg_price(symbol,1)
    sma50 = get_avg_price(symbol,50)
    sma200 = get_avg_price(symbol,200)
    #if (float(last_price) >= float(sma50) or float(last_price) >= float(sma200)) and float(last_price) >= 20:
    if float(last_price) >= float(sma50) or float(last_price) >= float(sma200):
        return True
    else:
        return False

def get_avg_price(symbol,day=200):
    """ 得到50天或者200天均线价格"""
    (db_cursor,cx) = connect_trade_db(symbol)
    if not db_cursor : return 0
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

def sort_stock(stock_data):
    """ 排序 """
    top_data = {}
    s_data = {}
    stock_list = []
    pool_data = []

    # 计算所有票子的平均涨跌幅
    avg_change = []
    stock_count = len(stock_data)
    for i in range(2,8):
        change = {}
        change[i] = 0
        for data in stock_data:
            inc_change = data[i]
            change[i] = change[i] + Decimal(inc_change)

        avg_ch = Decimal(change[i]) / Decimal(stock_count)
        avg_change.append(avg_ch)

    #if DEBUG : print  avg_change
    #if DEBUG: print "befor avg filter count = %s" % len(stock_data)
    # 过滤，低于平均涨幅的排除
    filter_data = []
    for data in stock_data:
        #for i in range(len(avg_change)):
        #    stock_change_index = i + 2
        #    if not Decimal(data[stock_change_index]) >= avg_change[i]:
        #        #print "symbol = %s ,filtered" % (data[0])
        #        break
        #if i+1 == len(avg_change):
        #    filter_data.append(data)    
        ########## 当前涨幅大于平均涨幅(权重大)
        #if not Decimal(data[len(avg_change)+1]) >= avg_change[len(avg_change)-1]:
        #    continue
        # 当前涨幅大于自身的平均涨幅
        #if not Decimal(data[7]) >= ((Decimal(data[2]) + Decimal(data[3]) + Decimal(data[4]) + Decimal(data[5]) + Decimal(data[6]) + Decimal(data[7]))/6):
        #    continue

        ################ 当前涨幅介于前期的最高值和最低值中间
        #max_inc = max(Decimal(data[2]),Decimal(data[3]),Decimal(data[4]),Decimal(data[5]),Decimal(data[6]),Decimal(data[7]))
        #min_inc = min(Decimal(data[2]),Decimal(data[3]),Decimal(data[4]),Decimal(data[5]),Decimal(data[6]),Decimal(data[7]))
        #if DEBUG: print "max = %s ,min = %s,current = %s" % (max_inc,min_inc,data[7])
        #if not (Decimal(data[7]) >= min_inc and Decimal(data[7]) < max_inc):
        #    continue

        filter_data.append(data)

    #if DEBUG: print "after avg filter count = %s" % len(filter_data)

    # 所有票子的排序
    for i in range(2,8):
        #sorted_list = sorted(stock_data, key=lambda result: Decimal(result[i]),reverse=True)
        sorted_list = sorted(filter_data, key=lambda result: Decimal(result[i]),reverse=True)
        count = 1
        for data in sorted_list:
            symbol = data[0]
            if not top_data.has_key(symbol):
                top_data[symbol] = count
                s_data[symbol] = data
            else:
                top_data[symbol] = top_data[symbol] + count
            count = count + 1
   
    sort_aa = sorted(top_data.items(),key=itemgetter(1))
    count = 1
    if DEBUG: print "Symbol\tbase\t10week\t8week\t6week\t4week\t2week\tlast\ttop_order"
    for item in sort_aa:
        symbol = item[0]
        top_order = item[1]
        stock_list.append(symbol)
        tmp_str = "%s,%s" % (symbol,count)
        tmp_data = tuple(tmp_str.split(","))
        pool_data.append(tmp_data)

        #print "symbol = %s , order = %s, top = %s" % (symbol,top_order,count)
        if DEBUG:
            print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (s_data[symbol]),
            print "\t%s" % count
        count = count +1

    return (stock_list,pool_data)

def update_stock(symbol):
    """
    重新更新有问题的数据
    """
    cache_dir = "%s/trade_db" % (base_dir)
    symbol = symbol.upper()
    db_file = "%s/%s" % (cache_dir,symbol)
    cmd = "rm -fr %s" % (db_file)
    os.system(cmd)
    cmd = "%s -s %s -d" % (update_cmd,symbol)
    os.system(cmd)

def sendmail(msg):
    """ send mail function """
    SERVER = 'localhost'
    FROM = 'hua.fu@alibaba-inc.com'
    TO = ['hunterfu2009@gmail.com']
    
    SUBJECT = 'Daily Stock Notify Report'
    # Prepare actual message
    message = """From: %s \nTo: %s\nSubject: %s \n
    %s """ % (FROM, ", ".join(TO), SUBJECT, msg)
    
    # Send the mail
    try:
        #server = smtplib.SMTP(host=SERVER,timeout=5)
        server = smtplib.SMTP(host=SERVER)
        server.sendmail(FROM, TO, message)
        server.quit()
    except Exception,e:
        print 'Unable to send email ErrorMsg=%s' % e


def usage():
    print '''
Usage: create_graph.py [options...]
Options: 
    -s/--signal_file                    : Stock signal file
    -r/--region                         : the special region of stock [CHINA|US|HK|TRACK]
    -e/--endday                         : scan stock endday [2011-10-1],default is today
    -h/--help                           : this help info page
    -d/--debug                          : run in debug mode 
    
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
    
    #各个变量保存
    scan_signal_file = "signal_file"
    stock_region =""
    timeframe ="day"
    endday = "today"
    global DEBUG
    DEBUG = False
    global base_index  
    base_index = {}
    base_index['CHINA'] = ["上证指数","000001.SS"] 
    base_index['US'] = ["标普500","^GSPC"] 
    global base_dir
    base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    stock_db = "%s/db/stock_db" % (base_dir)
    # 票池
    stock_pool = "%s/db/stock_pool" % (base_dir)
    # 筛选周期
    global peroid_offet
    peroid_offet = 20
    #peroid_offet_list = [15]
    #peroid_offet_list = [40,20,5]
    peroid_offet_list = [20,5]
    #peroid_offet_list = [20,5]

    conf_dir = "%s/conf" % (base_dir)
    template_file = "%s/template/stock_template.html" % (base_dir)
    global update_cmd
    update_cmd =  "%s/update_stock_data.py" % (base_dir)
    db_cursor = None
    cx = None
    (db_cursor,cx) = connect_db(stock_db)
    cx.text_factory=str
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],'dhs:r:e:')
    except getopt.GetoptError:
        usage()
        sys.exit()
    

    
    for opt, arg in opts: 
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt == '-s':
            scan_signal_file = arg
        elif opt == '-e':
            endday = arg
        elif opt == '-d':
            DEBUG = True
        elif opt == '-r':
            stock_region = arg
            stock_region = stock_region.upper()
        
    export_stock_symbol(db_cursor,cx)


    region = []
    if stock_region:
        if stock_region not in ['CHINA','US','HK','TRACK','TEST']:
            print "Input Region Not Correct,Please Check"
            sys.exit()
        region.append(stock_region)
    else:
        region = ['CHINA','US','HK','TRACK']
        os.system("rm -fr /home/hua.fu/geniustrader/output/*")
         
    for country in region:
        if country == 'TRACK':
            create_track_list(conf_dir,template_file,update_stock)
            continue

        wating_stock_list = get_stock_list(db_cursor,cx,country)
        #if DEBUG:   print "DEBUG = Before filter count = %s" % len(wating_stock_list)
        ##wating_stock_list = []
        ##wating_stock_list.append('000006.SZ')
        #stock_data = calc_stock(wating_stock_list,country)
        #(stock_list,pool_data) = sort_stock(stock_data)
        #if DEBUG:   print "DEBUG = After filter count = %s" % len(stock_list)
        ##if len(stock_list) > 50:
        ##    stock_list = stock_list[:50]

        for peroid in peroid_offet_list:
            peroid_offet = peroid
            if DEBUG:   print "DEBUG = Before filter count = %s" % len(wating_stock_list)
            stock_data = calc_stock(wating_stock_list,country)
            (stock_list,pool_data) = sort_stock(stock_data)
            if DEBUG:   print "DEBUG = After filter count = %s" % len(stock_list)
            wating_stock_list = stock_list
        # 跟新到票池数据库中
        new_list = []
        (pool_db_cursor,pool_cx) = connect_pool_db(stock_pool)
        pool_cx.text_factory=str
        lastupdate_time = int(time.time())
        for item in pool_data:
            try:
                sql_cmd = 'insert into stock values(NULL,"%s","%s","%s",%s,%s)' % (item[0],item[1],country,lastupdate_time,lastupdate_time)
                pool_db_cursor.execute(sql_cmd)
                new_list.append(item)
            except sqlite.IntegrityError,e:
                sql_cmd = "update stock set lastupdate_time = '%s',top_order = '%s' where symbol='%s'" % (lastupdate_time,item[1],item[0])
                pool_db_cursor.execute(sql_cmd)
            except Exception as inst:
                print "exception type = %sError = %s" % (type(inst),inst)
        pool_cx.commit()
        
        msg = None
        # 新加入的票
        if len(new_list) >0:
            print "new stock count = %s" % len(new_list)
            msg  = "========== new find stock count = %s =============\n\n" % len(new_list)
            msg = msg + "\nSymbol\tTop_Order"
            for item in new_list:
                print "Symbol = %s , top_order = %s" % (item[0],item[1])
                msg = msg + "\n%s\t%s" % (item[0],item[1])
        # 过期的票(连续2天没有更新)
        time_now = int(time.time())
        last_update_time = time_now - 86400 * 3
        sql = "select symbol,top_order from  stock where lastupdate_time <= %s and country = '%s'" % (last_update_time,country)
        pool_db_cursor.execute(sql)
        rs = pool_db_cursor.fetchall()
        if len(rs) >0:
            msg  = "========== delete stock count = %s =============\n\n" % len(rs)
            msg = msg + "\nSymbol\tTop_Order"
            for item in rs:
                msg = msg + "\n%s\t%s" % (item[0],item[1])

        pool_cx.close()

        if msg:
            if DEBUG: print "Send mail ======"
        #    sendmail(msg)            
        #create_graph(stock_list,template_file,conf_dir,country,scan_signal_file,endday)
    
if __name__ == "__main__":
    main()
    #calc_support_resistance('AIG')

