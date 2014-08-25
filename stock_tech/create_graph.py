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
from pprint import pprint
import commands
"""
创建符合条件的股票图表
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

def scan_stock(conf_dir,stock_region='US',signal_file="signal_file",timeframe="day",endday='today'):
    """ 
    根据给定的信号文件，扫描得出符合条件的股票
    扫描方法是 从月线开始 - > 周线 -> 日线 
    月线 看大趋势(投资)
    周线 看中期趋势(投机)
    日线 找买点(短线)
    信号文件命名:signal_name_month signal_name_week signal_name_day
    """
    #graph_dir = "/home/hua.fu/geniustrader/Scripts"
    graph_dir = script_dir
    stock_list = "%s/tmp/stock_%s_list" % (base_dir,stock_region)
    #stock_list = "%s/stock_%s_list" % (graph_dir,stock_region)
    # 测试列表
    if stock_region == 'TEST':
        stock_list = "%s/%s"  % (conf_dir,"stock_test_list")

    sig_file = "%s/%s" % (conf_dir,signal_file)
    #**************** 月线扫描 **************#
    #timeframe = "month"
    #sig_file="%s_%s" % (sig_file,timeframe)
    #if not os.path.isfile(sig_file): 
    #    print "Scan Signal File Not exists,please check %s" % (sig_file)
    #    sys.exit()
    #cmd = "cd %s;./scan.pl --nbprocess=2 --timeframe %s %s '%s' %s |sed -e '/^$/d' | sed -e '/Signal/d'" % (graph_dir,timeframe,stock_list,endday,sig_file)
    #print "CMD = %s" % cmd
    #res = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
    #print "DEBUG : stderr = %s " % res.stderr.readlines()
    #stock_line = res.stdout.readlines()
    #result_list = []
    #for line in stock_line:
    #    symbol = line.split('\t')[0]
    #    result_list.append(symbol)
    #
    #if len(result_list) == 0: 
    #    print "scan result is null"
    #    return result_list

    #return result_list

    #stock_list = "/tmp/tmp_stock_list.conf"
    #fd = open(ttock_list,"w")
    #fd.writelines(result_list)
    #fd.close()

    #**************** 周线扫描 **************#
    #timeframe = "week"
    #sig_file="%s_%s" % (sig_file,timeframe)
    #if not os.path.isfile(sig_file): 
    #    print "Scan Signal File Not exists,please check %s" % (sig_file)
    #    sys.exit()
    #cmd = "cd %s;./scan.pl --nbprocess=2 --timeframe %s %s '%s' %s |sed -e '/^$/d' | sed -e '/Signal/d'" % (graph_dir,timeframe,stock_list,endday,sig_file)
    #print "CMD = %s" % cmd
    #res = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
    #print "DEBUG : stderr = %s " % res.stderr.readlines()
    #stock_line = res.stdout.readlines()
    #result_list = []
    #for line in stock_line:
    #    symbol = line.split('\t')[0]
    #    result_list.append(symbol)
    #
    #if len(result_list) == 0: 
    #    print "scan result is null"
    #    return result_list
    #return result_list

    #stock_list = "/tmp/tmp_stock_list.conf"
    #fd = open(ttock_list,"w")
    #fd.writelines(result_list)
    #fd.close()

    #**************** 日线扫描 **************#
    #timeframe = "day"
    #sig_file="%s_%s" % (sig_file,timeframe)
    if not os.path.isfile(sig_file): 
        print "Scan Signal File Not exists,please check %s" % (sig_file)
        sys.exit()
    os.chdir('%s' % script_dir)
    cmd = "perl scan.pl --nbprocess=4 --timeframe %s %s '%s' %s |sed -e '/^$/d' | sed -e '/Signal/d'" % (timeframe,stock_list,endday,sig_file)
    print "CMD = %s" % cmd
    res = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    print "DEBUG : stderr = %s " % res.stderr.readlines()
    stock_line = res.stdout.readlines()
    result_list = []
    for line in stock_line:
        symbol = line.split('\t')[0]
        result_list.append(symbol)

    return result_list

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
    template = TemplateManager(precompile=0).prepare(template_file)
    tproc = TemplateProcessor(html_escape=0)
    stock = []
    for symbol in stock_list:
        symbol = symbol.strip()
        img_file = "%s/%s.png" % (out_dir,symbol)
        img_week_file = "%s/%s_WEEK.png" % (out_dir,symbol)
        img_month_file = "%s/%s_MONTH.png" % (out_dir,symbol)
        #if not os.path.isfile(img_file):
        #if calc_support_resistance(symbol,'day',template_graph_conf):
        #    graph_conf = template_graph_conf
        os.chdir('%s' % script_dir)
        #cmd = "cd %s;perl ./graphic.pl --file %s %s>%s" % (script_dir,graph_conf,symbol,img_file)
        cmd = "perl graphic.pl --file %s %s > %s" % (graph_conf,symbol,img_file)
        print cmd
        (status,output) = commands.getstatusoutput(cmd)
        #print "DEBUG graph_cmd = %s" % cmd
        #res = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        #print "DEBUG : stderr = %s " % res.stderr.readlines()
        #stock_line = res.stdout.readlines()
        #print stock_line
        (status,output) = commands.getstatusoutput(cmd)
        #sys.exit()
        cmd = "perl  graphic.pl --file %s %s > %s" % (graph_week_conf,symbol,img_week_file)
        #print "DEBUG graph_cmd = %s" % cmd
        (status,output) = commands.getstatusoutput(cmd)
        #res = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

        cmd = "perl  graphic.pl --file %s %s > %s" % (graph_month_conf,symbol,img_month_file)
        #print "DEBUG graph_cmd = %s" % cmd
        #res = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        (status,output) = commands.getstatusoutput(cmd)
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
 
def create_track_list(conf_dir,template_file,update_cmd):
    """ 生成追踪列表 """ 
    for track_list in ['track_stock_long.conf','track_stock_short.conf']:
        track_file = "%s/%s" % (conf_dir,track_list)
        fd = open(track_file)
        stock_list = fd.readlines()
        fd.close()
        for stock_symbol in stock_list:
            #cmd = "c:/Python27/python.exe %s -s %s -d" % (update_cmd,stock_symbol.strip())
            cmd = "python %s -s %s -d" % (update_cmd,stock_symbol.strip())
            #cmd = "%s -s %s -d" % (update_cmd,stock_symbol.strip())
            #print cmd
            if os.name != "posix":
                res = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                #print "DEBUG : stderr = %s " % res.stderr.readlines()
                stock_line = res.stdout.readlines()
                pprint(stock_line)
            else:
                os.system(cmd)
        create_graph(stock_list,template_file,conf_dir,"%s" % track_list) 

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
    homedir = get_home_path()
    sharenames = "%s/.gt/sharenames" % (homedir)
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


def export_stock(db_cursor,cx,stock_region='US'):
    """ 
    将符合条件的股票列表导出 
    """
    sql =""
    #time_now = int(time.time())
    time_now = int(time.time())
    sql = "select * from stock where stock_tradedb_lastupdate_time <= %s and stock_country = '%s' order by stock_symbol" % (time_now,stock_region)
    print "DEBUG sql = %s" % sql
    db_cursor.execute(sql)
    rs = db_cursor.fetchall()
    # print title
    if len(rs) == 0 : return
    filename = "%s/tmp/stock_%s_list" % (base_dir,stock_region)
    os.unlink(filename)
    stock_FILE = open(filename,"w")

    for item in rs:
        symbol = item[3]
        stock_FILE.writelines(symbol+ "\n")
        
    stock_FILE.close()


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
    global DEBUG,base_dir,img_out_dir,script_dir
    DEBUG = False
    base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    #homedir = get_home_path()
    #base_dir = "%s/stock_tech" % (homedir)
    stock_db = "%s/db/stock_db" % (base_dir)
    conf_dir = "%s/conf" % (base_dir)
    template_file = "%s/template/stock_template.html" % (base_dir)
    update_stock =  "%s/update_stock_data.py" % (base_dir)
    img_out_dir = "%s/img_out" % (base_dir)
    if not os.path.exists(img_out_dir):
        os.system("mkdir -p %s" % img_out_dir)
    script_dir = "%s/GeniusTrader/Scripts" % (base_dir)
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

        export_stock(db_cursor,cx,country)
        #if scan_signal_file:
        #    stock_list = scan_stock(conf_dir,country,scan_signal_file)
        #else:
        #    stock_list = scan_stock(conf_dir,country)
        if scan_signal_file.find("week") != -1:
            timeframe = "week"
        elif scan_signal_file.find("month") != -1:
            timeframe = "month"
        stock_list =  scan_stock(conf_dir,country,scan_signal_file,timeframe,endday)
        print "DEBUG : =COUNT = %s" % len(stock_list)
        print "DEBUG : =LIST == %s" % stock_list

        create_graph(stock_list,template_file,conf_dir,country,scan_signal_file,endday)
    
if __name__ == "__main__":
    main()
    #print get_home_path()

