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
"""
扫描符合条件的股票
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

def scan_stock(stock_list):
    """ 
    根据给定的股票列表，扫描得出符合条件的股票
    月线 看大趋势(投资)
    周线 看中期趋势(投机)
    日线 找买点(短线)
    """
    graph_dir = "/home/hua.fu/geniustrader/Scripts"
    ret_list = []
    if len(stock_list) == 0 : return ret_list
    #my_signal_tmp = """S:Generic:And \
    #{ Signals::Generic::Or \
    #    { S:Generic:Repeated { S:Generic:Below {I:Generic:PeriodAgo 1 {I:Prices HIGH}} %s } 20 } \
    #    { S:Generic:Repeated { S:Generic:Below {I:Generic:PeriodAgo 1 {I:Prices HIGH}} %s } 20 } \
    #}\
    #{ Signals::Generic::Or \
    #    { S:Generic:Above {I:Prices CLOSE} {I:EMA 50} }\
    #    { S:Generic:Above {I:Prices CLOSE} {I:EMA 200} }\
    #}\
    #{ Signals::Generic::Or \
    #    { S:Generic:Above {I:Prices CLOSE} %s }\
    #    { S:Generic:Above {I:Prices CLOSE} %s }\
    #} """
    my_signal_tmp = """S:Generic:Or \
    { Signals::Generic::And \
        { S:Generic:Repeated { I:Generic:PeriodAgo 1 { S:Generic:Below {I:Prices HIGH} %s} } 20}\
        { S:Generic:Above {I:Prices CLOSE} %s }\
    }\
    { Signals::Generic::And \
        { S:Generic:Repeated { I:Generic:PeriodAgo 1 { S:Generic:Below {I:Prices HIGH} %s} } 20}\
        { S:Generic:Above {I:Prices CLOSE} %s }\
    } """

    my_signal_sell_tmp = """S:Generic:Or \
    { Signals::Generic::And \
        { S:Generic:Repeated { I:Generic:PeriodAgo 1 { S:Generic:Above {I:Prices LOW} %s} } 20}\
        { S:Generic:Below {I:Prices CLOSE} %s }\
    }\
    { Signals::Generic::And \
        { S:Generic:Repeated { I:Generic:PeriodAgo 1 { S:Generic:Above {I:Prices LOW} %s} } 20}\
        { S:Generic:Below {I:Prices CLOSE} %s }\
    } """
    for symbol in stock_list:
        symbol = symbol.upper()
        pp_data = get_support_resistance(symbol,'day')
        FirstSupport = pp_data[1]
        SecondSupport = pp_data[2]
        FirstResistance = pp_data[3]
        SecondResistance= pp_data[4]
        #sig_file_str = my_signal_tmp % (FirstResistance,FirstResistance,SecondResistance,SecondResistance)
        sig_file_str = my_signal_sell_tmp % (FirstSupport,FirstSupport,SecondSupport,SecondSupport)
        sig_file = "/dev/shm/signal_%s" % (symbol)
        stock_list = "/dev/shm/%s" % (symbol)
        cmd = "echo %s > %s" % (symbol,stock_list)
        os.system(cmd)
        cmd ='echo "%s" >%s' % (sig_file_str,sig_file)
        os.system(cmd)
        cmd = "cd %s;./scan.pl --timeframe day %s 'today' %s |sed -e '/^$/d' | sed -e '/Signal/d'" % (graph_dir,stock_list,sig_file)
        res = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
        error_log = res.stderr.readlines() 
        if len(error_log) !=0:
            print "CMD = %s" % cmd
            print "DEBUG : stderr = %s " % res.stderr.readlines()
        stock_line = res.stdout.readlines()
        if not stock_line: continue
        symbol = stock_line[0].split('\t')[0]
        print "Symbol = %s ,Complete=====" % symbol
        ret_list.append(symbol.strip())

    return ret_list

def create_graph(stock_list,template_file,conf_dir,stock_region='US',signal_file="signal_file",endday='today'):
    """
    根据股票代码生成图片
    """
    out_dir = "/home/hua.fu/geniustrader/output"
    graph_conf = "%s/graph.conf" % (conf_dir)
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
        #if not os.path.isfile(img_file):
        if calc_support_resistance(symbol,'day',template_graph_conf):
            graph_conf = template_graph_conf
        cmd = "cd /home/hua.fu/geniustrader/Scripts;./graphic.pl --end '%s' --file %s --out '%s' %s" % (endday,graph_conf,img_file,symbol)
        #print "DEBUG graph_cmd = %s" % cmd
        (status,output) = commands.getstatusoutput(cmd)
        #cmd = "cd /home/hua.fu/geniustrader/Scripts;./graphic.pl --end '%s' --file %s --out '%s' %s" % (endday,graph_week_conf,img_week_file,symbol)
        if calc_support_resistance(symbol,'week',template_graph_conf):
            graph_week_conf = template_graph_conf 
        cmd = "cd /home/hua.fu/geniustrader/Scripts;./graphic.pl --file %s --out '%s' %s" % (graph_week_conf,img_week_file,symbol)
        #print "DEBUG graph_cmd = %s" % cmd
        (status,output) = commands.getstatusoutput(cmd)

        #cmd = "cd /home/hua.fu/geniustrader/Scripts;./graphic.pl --file %s --out '%s' %s" % (graph_month_conf,img_month_file,symbol)
        #print "DEBUG graph_cmd = %s" % cmd
        #(status,output) = commands.getstatusoutput(cmd)

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
 
def create_track_list(conf_dir,template_file,update_cmd):
    """ 生成追踪列表 """ 
    track_file = "%s/track_stock.conf" % (conf_dir)
    fd = open(track_file)
    stock_list = fd.readlines()
    fd.close()
    for stock_symbol in stock_list:
       cmd = "%s -s %s -d" % (update_cmd,stock_symbol.strip()) 
       #print cmd
       os.system(cmd)
    create_graph(stock_list,template_file,conf_dir,"TRACK") 

def create_test_list(conf_dir,template_file,update_cmd):
    """ 测试列表 """ 
    track_file = "%s/test_stock.conf" % (conf_dir)
    fd = open(track_file)
    stock_list = fd.readlines()
    fd.close()
    create_graph(stock_list,template_file,conf_dir,"TEST") 

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
    #sql = "select * from stock where stock_tradedb_lastupdate_time <= %s and stock_country = '%s' ORDER BY RANDOM() limit 200" % (time_now,stock_region)
    db_cursor.execute(sql)
    rs = db_cursor.fetchall()
    if len(rs) == 0 : return
    stock_list = []
    for item in rs:
        symbol = item[3]
        stock_list.append(symbol)
    return stock_list

def calc_support_resistance(symbol,timeframe='day',template_graph_conf="/tmp/graph.conf"):
    """
    计算阻力位和支撑位(轴心交易),使用周和月的
    日线图用 周的，周线图用 月的
    """
    graph_conf = None
    base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    conf_dir = "%s/conf" % (base_dir)
    if timeframe == "day":
        graph_conf = "%s/graph_template_%s.conf" % (conf_dir,timeframe)
        timeframe = "week"
    elif timeframe == "week":
        graph_conf = "%s/graph_template_%s.conf" % (conf_dir,timeframe)
        timeframe = "month"

    symbol = symbol.upper()
    cmd = "cd /home/hua.fu/geniustrader/Scripts;./display_indicator.pl --last-record --tight --timeframe=%s I:PP %s|grep -P '\[\d+[-/]\d+\]'" % (timeframe,symbol)
    #print "DEBUG indicator_cmd = %s" % cmd
    (status,output) = commands.getstatusoutput(cmd)
    if status != 0:
        return False
    pivot_data = output.split("=")[1].split("\t")[1:]
    #print "pivot_data = %s" % pivot_data
    fd = open(graph_conf)
    source_line = fd.readlines()
    replace_content = [] 
    fd.close()
    for line in source_line: 
        #print line
        myrep = None
        if line.find('CenterPrice') != -1:
            myrep = line.replace('CenterPrice',fpformat.fix(pivot_data[0],2))
        if line.find('FirstSupport') != -1:
            myrep = line.replace('FirstSupport',fpformat.fix(pivot_data[1],2))
        if line.find('SecondSupport') != -1:
            myrep = line.replace('SecondSupport',fpformat.fix(pivot_data[2],2))
        if line.find('FirstResistance') != -1:
            myrep = line.replace('FirstResistance',fpformat.fix(pivot_data[3],2))
        if line.find('SecondResistance') != -1:
            myrep = line.replace('SecondResistance',fpformat.fix(pivot_data[4],2))
        if myrep:
            replace_content.append(myrep)
        else:
            replace_content.append(line)

    tmp_file = template_graph_conf
    fd = open(tmp_file,"w")
    fd.writelines(replace_content)
    fd.close()
    return True


def get_support_resistance(symbol,timeframe='day'):
    """
    计算阻力位和支撑位(轴心交易),使用周和月的
    日线图用 周的，周线图用 月的
    """
    if timeframe == "day":
        timeframe = "week"
    elif timeframe == "week":
        timeframe = "month"
    symbol = symbol.upper()
    cmd = "cd /home/hua.fu/geniustrader/Scripts;./display_indicator.pl --last-record --tight --timeframe=%s I:PP %s|grep -P '\[\d+[-/]\d+\]'" % (timeframe,symbol)
    (status,output) = commands.getstatusoutput(cmd)
    if status != 0: 
        return False
    pivot_data = output.split("=")[1].split("\t")[1:]
    return pivot_data

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
    
    base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    stock_db = "%s/db/stock_db" % (base_dir)
    conf_dir = "%s/conf" % (base_dir)
    template_file = "%s/template/stock_template.html" % (base_dir)
    update_stock =  "%s/update_stock_data.py" % (base_dir)
    db_cursor = None
    cx = None
    (db_cursor,cx) = connect_db(stock_db)
    cx.text_factory=str
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],'dhs:r:e:')
    except getopt.GetoptError:
        usage()
        sys.exit()
    
    #各个变量保存
    scan_signal_file = "signal_file"
    stock_region =""
    timeframe ="day"
    endday = "today"
    global DEBUG
    DEBUG = False

    
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
        stock_list = scan_stock(wating_stock_list)
        print "DEBUG : =COUNT = %s" % len(stock_list)
        print "DEBUG : =LIST == %s" % stock_list

        create_graph(stock_list,template_file,conf_dir,country,scan_signal_file,endday)
    
if __name__ == "__main__":
    main()
    #calc_support_resistance('AIG')

