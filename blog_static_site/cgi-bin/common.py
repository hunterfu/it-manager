#!/opt/bin/python
# -*- coding: utf-8 -*-
__author__ = "HunterFu"
__email__ = "hua.fu@alibaba-inc.com"
__status__ = "Production"


import urllib,os,sys
import json
import datetime
import shutil
import pickle
import time
import pysqlite2.dbapi2 as sqlite
# for debug
from pprint import pprint

"""
This is the for stock select prog
"""
cache_dir = "/tmp"
global base_dir
base_dir = "/home/hua.fu/it-manager/stock_tech"
# 筛选后的列表
stock_pool = "%s/db/stock_pool" % (base_dir)
# 所有列表数据库
stock_db = "%s/db/stock_db" % (base_dir)

def set_key(key,data):
    '''
    set cache to file
    '''
    cache_file = "%s/%s" % (cache_dir,key)
    fout = open(cache_file, "w")
    pickle.dump(data, fout, protocol=0)
    fout.close()


def get_data(key,exprtime):
    '''
    get data from file cache,默认1天过期
    '''
    cache_file = "%s/%s" % (cache_dir,key)
    if not os.path.isfile(cache_file) or (int(time.time()) - int(os.stat(cache_file).st_mtime) >= exprtime):
        return False

    if os.path.isfile(cache_file):
        fin = open(cache_file, "r")
        data  = pickle.load(fin)
        fin.close()
        return data


def connect_db(db_file):
    '''
    connect sqlite db
    '''
    if os.path.isfile(db_file):
        cx = sqlite.connect(db_file)
        cu = cx.cursor()
        return (cu,cx)
    else:
        return (False,False)

def connect_trade_db(symbol):
    """
    连接stock数据库
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

def stock_symbol2name_dict():
    """ 
    导出股票代码名称对应代码表 
    """
    (db_cursor,cx) = connect_db(stock_db)
    sql = "select * from stock order by stock_symbol"
    db_cursor.execute(sql)
    rs = db_cursor.fetchall()
    ret_dict = {}
    if len(rs) == 0 : return ret_list
    for item in rs:
        title = item[2]
        symbol = item[3]
        if title:
            ret_dict[symbol]  = title
        else:
            ret_dict[symbol] = "No title"
    cx.close()
    return ret_dict

def stocklist_bysignal():
    '''
    获取系统发现的stock列表
    '''
    symbol2title = stock_symbol2name_dict()
    (db_cursor,cx) = connect_db(stock_pool)
    sql = "select * from stock"
    db_cursor.execute(sql)
    rs = db_cursor.fetchall()
    ret_list = []
    if len(rs) == 0 : return ret_list
    for item in rs:
        stock_data = {}
        stock_data['diff_day'] = (item[5] - item[4]) / 24 / 3600
        # 如果发现时间持续过短，说明不够强
        if stock_data['diff_day'] <= 2: continue

        stock_data['symbol'] = item[1]
        if symbol2title.has_key(item[1]):
            stock_data['title'] = symbol2title[item[1]]
        else:
            stock_data['title'] = item[1]
        stock_data['top_order'] = item[2]
        stock_data['country'] = item[3]
        stock_data['firstsee_time'] =  time.strftime("%Y-%m-%d",time.localtime(item[4]))
        stock_data['lastupdate_time'] = time.strftime("%Y-%m-%d",time.localtime(item[5]))
        ret_list.append(stock_data)
    cx.close()
    return ret_list

def get_stock_list():
    '''
    返回列表 加上Cache
    '''
    key = "list_by_signal"
    #stock_list = get_data(key,86400)
    #if not stock_list:
    #    stock_list =  stocklist_bysignal()
    #    set_key(key,stock_list)
    #return stock_list
    stock_list =  stocklist_bysignal()
    return stock_list

def get_stock_price(symbol="C"):
    '''
    返回股票价格数据
    '''
    (db_cursor,cx) = connect_trade_db(symbol)
    sql = "select s_date,s_close from stock order by s_date  DESC limit 65"
    db_cursor.execute(sql)
    rs = db_cursor.fetchall()
    ret_list = []
    if len(rs) == 0 : return ret_list
    sorted_list = sorted(rs, key=lambda result: result[0])
    for item in sorted_list:
        price_data = {}
        #price_data['symbol'] = symbol
        #daytime = datetime.datetime.strptime(item[0],"%Y-%m-%d")
        #seconds = int(time.mktime(daytime.timetuple()))
        #price_data['date'] = seconds
        price_data['date'] = item[0]
        price_data['close'] = item[1]
        price_data['previousClose'] = "48.02"
        ret_list.append(price_data)
    cx.close()
    return ret_list

if __name__ == '__main__':
    ''' for unit test '''
    data = get_stock_price()
    pprint(data)
