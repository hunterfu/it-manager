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
import smtplib
from pprint import pprint

"""
股票均线相对大盘均线的涨幅比较
针对大盘指数涨跌幅对比
"""
import threading,Queue

class ind_runs(threading.Thread):
    def __init__(self,base,long_result,short_result,day_ago,sma_day,timeframe='day'):  
        threading.Thread.__init__(self)    
        self.long_result=long_result
        self.short_result=short_result
        self.base=base
        self.day_ago= day_ago
        self.sma_day=sma_day
        self.timeframe = timeframe # week,day,month

    def run(self):
        """
        强弱度＝（该股涨跌幅-指数涨跌幅）*100
        """
        while  clientpool.empty() != True:
            try:
                symbol = clientpool.get(block=0)
                change = get_indicator_output(symbol,self.day_ago,self.sma_day,self.timeframe)
                if change >= self.base:
                    tmp_str = "%s,%s" % (symbol,change)
                    data = tuple(tmp_str.split(","))
                    self.long_result.append(data)
                if change <= self.base:
                    tmp_str = "%s,%s" % (symbol,change)
                    data = tuple(tmp_str.split(","))
                    self.short_result.append(data)
                
            except Queue.Empty:
                pass

class graph_runs(threading.Thread):
    def __init__(self,result,endday,conf_dir):
        threading.Thread.__init__(self)
        self.result=result
        self.endday = endday
        self.conf_dir = conf_dir

    def run(self):
        while  clientpool.empty() != True:
            try:
                symbol = clientpool.get(block=0)
                out_dir = img_out_dir
                conf_dir = self.conf_dir
                graph_conf = "%s/graph_day.conf" % (conf_dir)
                graph_week_conf = "%s/graph_week.conf" % (conf_dir)
                graph_month_conf = "%s/graph_month.conf" % (conf_dir)
                img_file = "%s/%s.png" % (out_dir,symbol)
                img_week_file = "%s/%s_WEEK.png" % (out_dir,symbol)
                img_month_file = "%s/%s_MONTH.png" % (out_dir,symbol)
                os.chdir('%s' % script_dir)
                cmd = "perl graphic.pl --end '%s' --file %s --out '%s' %s" % (self.endday,graph_conf,img_file,symbol)
                (status,output) = commands.getstatusoutput(cmd)
                if status != 0 : 
                    print "Error = %s" % output 
                    continue
                cmd = "perl graphic.pl --file %s --out '%s' %s" % (graph_week_conf,img_week_file,symbol)
                (status,output) = commands.getstatusoutput(cmd)
                if status != 0: 
                    print "Error = %s" % output 
                    continue
                cmd = "perl graphic.pl --file %s --out '%s' %s" % (graph_month_conf,img_month_file,symbol)
                (status,output) = commands.getstatusoutput(cmd)
                if status != 0: 
                    print "Error = %s" % output 
                    continue
                stock_dict= {}
                stock_dict['symbol'] = symbol
                stock_dict['img'] = img_file
                stock_dict['img_week'] = img_week_file
                stock_dict['img_month'] = img_month_file
                self.result.append(stock_dict)
            except Queue.Empty:
                pass

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
            country varchar(100),
            firstsee_time NUMERIC DEFAULT 0,
            lastupdate_time NUMERIC DEFAULT 0
            )''')
        return (cu,cx)


def calc_stock(stock_list,country,timeframe='day'):
    """ 
    计算rps
    """
    graph_dir = script_dir
    long_data = []
    short_data = []
    if len(stock_list) == 0 : return result_data
    # 标普500指数作为基准
    index_name = base_index[country][0]
    index_symbol = base_index[country][1]
    #day_ago = 30
    #sma_day = 120
    base_line_percent = get_indicator_output(index_symbol,day_ago,sma_day,timeframe)
    if DEBUG: print "day_ago = %s , sma_day = %s ,timeframe=%s , base_line =%s " % (day_ago,sma_day,timeframe,base_line_percent)
    #stock_list.append(index_symbol)
    quene_list = []
    ts = []
    # 多线程运行
    global clientpool 
    clientpool = Queue.Queue(0)
    for a in stock_list:
        a=a.strip()
        clientpool.put(a)

    for b in xrange(20):
        t = ind_runs(base_line_percent,long_data,short_data,day_ago,sma_day,timeframe)
        t.start()
        ts.append(t)
    for t in ts:
        if t:t.join()

    return (long_data,short_data)


def create_graph(stock_list,template_file,conf_dir,stock_region='US',signal_file="signal_file",endday='today'):
    """
    根据股票代码生成图片
    """
    out_dir = img_out_dir
    graph_conf = "%s/graph_day.conf" % (conf_dir)
    template_graph_conf = "/tmp/graph_%s.conf" % (signal_file)
    graph_week_conf = "%s/graph_week.conf" % (conf_dir)
    graph_month_conf = "%s/graph_month.conf" % (conf_dir)
    stock_count = len(stock_list)
    template = TemplateManager().prepare(template_file)
    tproc = TemplateProcessor(html_escape=0)
    stock = []
    for symbol in stock_list:
        img_file = "%s/%s.png" % (out_dir,symbol)
        img_week_file = "%s/%s_WEEK.png" % (out_dir,symbol)
        img_month_file = "%s/%s_MONTH.png" % (out_dir,symbol)
        stock_dict= {}
        stock_dict['symbol'] = symbol
        stock_dict['img'] = img_file
        stock_dict['img_week'] = img_week_file
        stock_dict['img_month'] = img_month_file
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

     # 多线程运行
    global clientpool 
    #globals()['clentpool'] = Queue.Queue(0)
    clientpool = Queue.Queue(0)
    ts = []
    for a in stock_list:
        a=a.strip()
        clientpool.put(a)

    for b in xrange(20):
        t = graph_runs(stock,endday,conf_dir)
        t.start()
        ts.append(t)
    for t in ts:
        if t:t.join()

 
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

def sort_stock(stock_data):
    """ 排序 """
    top_data = {}
    s_data = {}
    stock_list = []
    pool_data = []

    # 所有票子的排序
    if action == "long":
        sorted_list = sorted(stock_data, key=lambda result: Decimal(result[1]),reverse=True)
    if action == "short":
        sorted_list = sorted(stock_data, key=lambda result: Decimal(result[1]))
    for item in sorted_list:
        symbol = item[0]
        stock_percent = item[1]
        stock_list.append(symbol)
        tmp_str = "%s,%s" % (symbol,stock_percent)
        tmp_data = tuple(tmp_str.split(","))
        pool_data.append(tmp_data)

    return (stock_list,pool_data)

def get_indicator_output(symbol,dayago=65,sma=50,timeframe='day'):
    """
    """
    symbol = symbol.upper()
    ##if DEBUG: print "DEBUG : CURRENT pROCESS SYMBOL=%s" % symbol
    #print "DEBUG : CURRENT pROCESS SYMBOL=%s" % symbol
    os.chdir('%s' % script_dir) 
    if timeframe == 'day':
        cmd = "perl display_indicator.pl  --timeframe=%s --nb=%s \
                --tight I:SMA %s %s|grep -P '\[\d+-\d+\-\d+]*.*'" % (timeframe,dayago,symbol,sma)
                
    if timeframe == 'week':
        cmd = "perl display_indicator.pl  --timeframe=%s --nb=%s \
                --tight I:SMA %s %s|grep -P '\[\d+-\d+]*.*'" % (timeframe,dayago,symbol,sma)

    if timeframe == 'month':
        cmd = "perl display_indicator.pl  --timeframe=%s --nb=%s \
                --tight I:SMA %s %s| grep -P '\[\d+\/\d+]*.*'" % (timeframe,dayago,symbol,sma)

    #print "DEBUG indicator_cmd = %s" % cmd
    (status,output) = commands.getstatusoutput(cmd)
    if status != 0:
        return False
    ind_list = output.split("\n")
    base_point = ind_list[0].split("=")[1].strip()
    if base_point !="":
        last_point = ind_list[len(ind_list)-1].split("=")[1].strip()
        change = (Decimal(last_point) - Decimal(base_point))/Decimal(base_point) * 100
        change = Decimal(str(round(change, 3)))
    else:
        change = 0
    return change

def scan_stock(conf_dir,stock_list,signal_file):
    """ 
    """
    graph_dir = "/home/hua.fu/geniustrader/Scripts"
    ret_list = []
    if len(stock_list) == 0 : return ret_list
    timeframe="day"
    if signal_file.find("week") != -1:
        timeframe = "week"
    elif signal_file.find("month") != -1:
        timeframe = "month"

    sig_file = "%s/%s" % (conf_dir,signal_file)
    filename = "/dev/shm/%s" % (signal_file)
    stock_FILE = open(filename,"w")
    for symbol in stock_list:
        stock_FILE.writelines(symbol+ "\n")
    stock_FILE.close()

    cmd = "cd %s;./scan.pl --nbprocess=4 --timeframe %s %s 'today' %s |sed -e '/^$/d' | sed -e '/Signal/d'" % (graph_dir,timeframe,filename,sig_file)
    res = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
    error_log = res.stderr.readlines() 
    if len(error_log) !=0:
        print "CMD = %s" % cmd
        print "DEBUG : stderr = %s " % res.stderr.readlines()
    for line in  res.stdout.readlines():
        symbol = line.split('\t')[0]
        ret_list.append(symbol.strip())

    return ret_list

def create_stock_list(stock_list,stock_region='US'):
    """ 
    将符合条件的股票列表导出 
    """
    filename = "/home/hua.fu/geniustrader/Scripts/stock_%s_list" % (stock_region)
    stock_FILE = open(filename,"w")

    for symbol in stock_list:
        stock_FILE.writelines(symbol+ "\n")
        
    stock_FILE.close()

def filter_by_indicator(stock_list):
    """
    根据技术指标筛选短期强于大盘的股票
    """
    filter_signal_file = ['buy_filter_signal_month']
    for sig_file in filter_signal_file:
        stock_list = scan_stock(conf_dir,stock_list,sig_file)
    if DEBUG: print "DEBUG: After Scan = %s" % len(stock_list)
    return stock_list

def update_filter_stockdb(stock_db,data,country):
    """
    将符合条件的股票保存到后续观察票池中
    """
    new_list = []
    (pool_db_cursor,pool_cx) = connect_pool_db(stock_db)
    pool_cx.text_factory=str
    lastupdate_time = int(time.time())
    for symbol in data:
        try:
            sql_cmd = 'insert into stock values(NULL,"%s","%s",%s,%s)' % (symbol,country,lastupdate_time,lastupdate_time)
            pool_db_cursor.execute(sql_cmd)
            new_list.append(symbol)
        except sqlite.IntegrityError,e:
            sql_cmd = "update stock set lastupdate_time = '%s' where symbol='%s'" % (lastupdate_time,symbol)
            pool_db_cursor.execute(sql_cmd)
        except Exception as inst:
            print "exception type = %s,Error = %s" % (type(inst),inst)
    pool_cx.commit()

def get_buy_point(stock_db,buy_signal,country):
    """
    扫描票池数据库,找到日线图买点
    """
    (db_cursor,pool_cx) = connect_pool_db(stock_db)
    pool_cx.text_factory=str
    # 获取列表
    sql = "select symbol from stock where country='%s'" % (country) 
    db_cursor.execute(sql)
    rs = db_cursor.fetchall()
    if len(rs) == 0 : return
    stock_list = []
    for item in rs:
        symbol = item[0]
        stock_list.append(symbol)
    pool_cx.close()
    # 扫描列表
    scan_list = scan_stock(conf_dir,stock_list,buy_signal)
    if DEBUG: print "DEBUG: Buy Point Signal = %s ,After Scan = %s" % (buy_signal,len(scan_list))
    return scan_list

def compare_to_spy(wating_stock_list,peroid_offet_list,country):
    """
    根据个股与大盘对比，选取强于大盘的个股
    """
    cache_file = "%s/tmp/filter_%s" % (base_dir,country)
    if not os.path.isfile(cache_file) or (int(time.time()) - int(os.stat(cache_file).st_mtime) >= 86000):
        for peroid in peroid_offet_list:
            (globals()['day_ago'],globals()['sma_day'],timeframe)  = peroid
            if DEBUG:   print "DEBUG = Before filter count = %s" % len(wating_stock_list)
            (long_stock_data,short_data) = calc_stock(wating_stock_list,country,timeframe)
            (stock_list,pool_data) = sort_stock(long_stock_data)
            if DEBUG:   print "DEBUG = After filter count = %s" % len(stock_list)
            wating_stock_list = stock_list

        fout = open(cache_file, "w")
        pickle.dump(stock_list, fout, protocol=0)
        fout.close()
        return stock_list
    elif os.path.isfile(cache_file):
        fin = open(cache_file, "r")
        data  = pickle.load(fin)
        fin.close()
        return data


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
    -s/--action                         : long or short
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
    #global clientpool,action
    global DEBUG
    DEBUG = False
    global base_index  
    base_index = {}
    base_index['CHINA'] = ["上证指数","000001.SS"] 
    base_index['US'] = ["标普500","^GSPC"] 
    global base_dir,action,img_out_dir,script_dir
    base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    img_out_dir = "%s/img_out" % (base_dir)
    script_dir = "%s/GeniusTrader/Scripts" % (base_dir)
    stock_db = "%s/db/stock_db" % (base_dir)
    # 票池
    stock_pool = "%s/db/stock_pool" % (base_dir)
    # 筛选周期
    global day_ago,sma_day,conf_dir
    (day_ago,sma_day) = (30,200)
    peroid_offet_list = [(30,200,'day'),(30,50,'day')]

    conf_dir = "%s/conf" % (base_dir)
    template_file = "%s/template/stock_template.html" % (base_dir)
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

    if not scan_signal_file:
        print "please setting long or short using -s"
        sys.exit()
    if scan_signal_file not in ['long','short']:
        print "Input Action Not Correct,Please Check"
        sys.exit()
    action = scan_signal_file
    region = []
    if stock_region:
        if stock_region not in ['CHINA','US','HK']:
            print "Input Region Not Correct,Please Check"
            sys.exit()
        region.append(stock_region)
    else:
        region = ['CHINA','US','HK']
        os.system("rm -fr /home/hua.fu/geniustrader/output/*")
         
    for country in region:
        #stock_list=['A','FSLR']
        #create_graph(stock_list,template_file,conf_dir,country,"TESsig_file",endday)
        #sys.exit(0)
        # 根据大盘过滤出强于大盘的个股
        wating_stock_list = get_stock_list(db_cursor,cx,country)
        stock_list = compare_to_spy(wating_stock_list,peroid_offet_list,country)
        stock_list = stock_list[:50]
        create_graph(stock_list,template_file,conf_dir,country,"all",endday)
        sys.exit(0)

        # 根据月线过滤kdj再底部cross的
        wating_stock_list = get_stock_list(db_cursor,cx,country)
        stock_list = wating_stock_list
        data = filter_by_indicator(stock_list)
        create_graph(data,template_file,conf_dir,country,"all",endday)
        sys.exit(0)
        # 更新到票池数据库中
        update_filter_stockdb(stock_pool,data,country)
        # 跟踪扫描日线，找到买点
        filter_signal_file = ['buy_point_signal_one','buy_point_signal_two','buy_point_signal_three']
        for sig_file in filter_signal_file:
            stock_list = get_buy_point(stock_pool,sig_file,country)
            # 画图
            if len(stock_list) > 0:
                create_graph(stock_list,template_file,conf_dir,country,sig_file,endday)
        #create_stock_list(stock_list,country)
        #sys.exit(0)
    
if __name__ == "__main__":
    main()
    #sys.exit(0)
    #stocklist = ['A','BAC','FSLR']
    #filter_list = scan_stock("/home/hua.fu/it-manager/stock_tech/conf",stocklist,"buy_signal_kdj_cross_month","US")
    #print filter_list
    #print get_indicator_output('000001.SS',30,30,'day')
    #print get_indicator_output('^GSPC',30,30,'week')
    #print get_indicator_output('^GSPC',30,30,'month')
    #result_data = []
    #stocklist = ['A','BAC','FSLR']
    #t = ind_runs(-10,result_data,stocklist)
    #t.start()
    #threading.Thread.join(t) 
    #print result_data
            


