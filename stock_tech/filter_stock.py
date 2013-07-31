#!/usr/bin/env python
# -*- coding: utf-8 -*-
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


def request_one(cache_file):
    """ get data from google """

    stock_exchange = '((exchange == "NYSE") | (exchange == "NASDAQ") | (exchange == "AMEX"))'
    stock_roi_ttm="(return_on_investment_year >= 0)"  #上年投资回报率
    stock_volume = " (volume >= 0)"
    stock_avg_volume = "(average_volume >= 200000)"
    stock_price = "(last_price >= 1.5)"
    stock_50_avg = "(average_50day_price >= 0)" 
    stock_200_avg = "(average_200day_price >= 0)"
    stock_dps = "(dividend_yield >= 0)"     #股息收益率
    stock_eps = "(earnings_per_share >= 0)"  # 每股收益
    stock_bps = "(book_value_per_share_year >= 0)" # 每股净资产(上年)
    stock_cashpershare = "(cash_per_share_year >= 0)" # 每股现金流上年
    stock_debt2equity = "(total_debt_to_equity_year >= 0)" # 总负债/股东权益比(上年) 
    stock_ldept2equity = "(longterm_debt_to_equity_year >= 0)" # 长期负债/股东权益比(上年) 
    stock_debt2asset = "(total_debt_to_assets_year >= 0)" # 资产负债率(上年) 

    q = "[%s & %s & %s & %s & %s & %s & %s & %s & %s & %s & %s & %s & %s & %s]" % (stock_exchange,stock_roi_ttm,stock_volume,stock_avg_volume,stock_price,stock_50_avg,stock_200_avg,stock_dps,stock_eps,stock_bps,stock_cashpershare,stock_debt2equity,stock_ldept2equity,stock_debt2asset)
    #q = '[((exchange == "NYSE") | (exchange == "NASDAQ") | (exchange == "AMEX")) & (dividend_yield >= 0) & (price_to_book >= 0)]'
    q = urllib.quote(q)
    url = 'http://www.google.com/finance?gl=us&hl=en&output=json&start=0&num=3000&noIL=1&q=%s&restype=company' % q

    #myopener = MyOpener()
    f = urllib.urlopen(url)
    #f = myopener.urlopen(url)
    #myopener.retrieve(url,cache_file)
    content = f.readlines()
    fout = open(cache_file, "w")
    for line in content:
        fout.write(line)
    fout.close()
    return True

def request_two(cache_file):
    """ get data from google """

    stock_exchange = "((exchange:NYSE) OR (exchange:NASDAQ) OR (exchange:AMEX))"
    stock_roi_ttm="(ReturnOnInvestmentYear > 0 | ReturnOnInvestmentYear = 0)"  #上年投资回报率
    stock_volume = " (Volume > 0 | Volume = 0)"
    stock_avg_volume = "(AverageVolume > 200000 | AverageVolume = 200000)"
    stock_price = "(QuoteLast > 1.5 | QuoteLast = 1.5)"
    stock_50_avg = "(Price50DayAverage > 0 | Price50DayAverage = 0)" 
    stock_200_avg = "(Price200DayAverage > 0 | Price200DayAverage = 0)"
    stock_dps = "(DividendYield > 0 | DividendYield = 0)"   # 股息收益率
    stock_eps = "(EPS > 0| EPS = 0)"  # 每股收益
    stock_bps = "(BookValuePerShareYear > 0 | BookValuePerShareYear = 0)" # 每股净资产(上年)
    stock_cashpershare = "(CashPerShareYear > 0 | CashPerShareYear = 0)" # 每股现金流上年
    stock_debt2equity = "(TotalDebtToEquityYear > 0 | TotalDebtToEquityYear = 0)" # 总负债/股东权益比(上年) 
    stock_ldept2equity = "(LTDebtToEquityYear > 0 | LTDebtToEquityYear = 0)" # 长期负债/股东权益比(上年) 
    stock_debt2asset = "(TotalDebtToAssetsYear > 0 | TotalDebtToAssetsYear = 0)" # 资产负债率(上年) 

    q = "%s [%s & %s & %s & %s & %s & %s & %s & %s & %s & %s & %s & %s & %s]" % (stock_exchange,stock_roi_ttm,stock_volume,stock_avg_volume,stock_price,stock_50_avg,stock_200_avg,stock_dps,stock_eps,stock_bps,stock_cashpershare,stock_debt2equity,stock_ldept2equity,stock_debt2asset)
    q = urllib.quote(q)
    url = 'http://www.google.com/finance?&gl=us&hl=en&output=json&start=0&num=3000&noIL=1&q=%s&restype=company' % q
    f = urllib.urlopen(url)
    content = f.readlines()
    fout = open(cache_file, "w")
    for line in content:
        fout.write(line)
    fout.close()
    return True
    
def request(cache_file):
    if not os.path.isfile(cache_file) or (int(time.time()) - int(os.stat(cache_file).st_mtime) >= 86400):
        have_data = False
        method_list = ['one','two']
        for method in method_list:
            func = "request_%s(cache_file)" % (method)
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

def analyse_stock(stock_data_list):
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
        field_data_list = stock_data['columns'] 
        for field_data in field_data_list:
            field = field_data['field'] 
            val =  field_data['value']
            stock_dict[field] = val
        stock_list.append(stock_dict)

    return stock_list 


def connect_db(db_file):
    """
    connect db
    """
    if os.path.isfile(db_file):
        cx = sqlite.connect(db_file)
        cu = cx.cursor()
        return (cu,cx)
    else:
        #create
        cx = sqlite.connect(db_file)
        cu = cx.cursor()
        cu.execute('''
            create table stock(
            id integer primary key,
            exchange_name varchar(20),
            stock_title varchar(50),
            stock_symbol varchar(20),
            stock_price NUMERIC,
            stock_50_avg NUMERIC,
            stock_200_avg NUMERIC,
            stock_volume INTEGER,
            stock_avg_volume INTEGER,
            stock_eps NUMERIC,
            stock_bps NUMERIC,
            stock_dps NUMERIC,
            stock_roi_ttm NUMERIC,
            stock_earning_yield NUMERIC,
            stock_bps_yield NUMERIC,
            stock_cashpershare NUMERIC,
            stock_cash_yield NUMERIC,
            stock_debt2equity NUMERIC,
            stock_ldebt2equity NUMERIC,
            stock_debt2asset NUMERIC,
            stock_note varchar(1000)
            )''')
        return (cu,cx)


def update_db(db_cursor,cx,stock_list):
    """ update db from json file """
    # del data from db
    sql_cmd = "delete from stock"
    db_cursor.execute(sql_cmd)
    cx.commit()
    # insert db
    for stock_dict in stock_list:
        # determin record is already in db or not
        stock_exchange = stock_dict['exchange']
        stock_symbol = stock_dict['symbol']
        stock_title = stock_dict['title']
        note = stock_filter(stock_dict)
        if not note: continue
        #print stock_dict
        #stock_roi_ttm = stock_dict['ReturnOnInvestmentTTM'].replace(",","")
        stock_roi_ttm = stock_dict['ReturnOnInvestmentYear'].replace(",","")
        #stock_volume = stock_dict['Volume'].replace(",","") 
        #stock_avg_volume = stock_dict['AverageVolume'].replace(",","")
        stock_volume = "0"
        stock_avg_volume = "0"
        stock_price = stock_dict['QuoteLast'] 
        stock_50_avg = stock_dict['Price50DayAverage'] 
        stock_200_avg = stock_dict['Price200DayAverage'] 
        stock_eps = stock_dict['EPS'] 
        stock_bps = stock_dict['BookValuePerShareYear']
        #stock_dps = stock_dict['DividendPerShare'] 
        stock_dps = stock_dict['DividendYield'] #股息收益率 
        #stock_epsgrowthrate = stock_dict['EPSGrowthRate5Years']
        #stock_revenuegrowthrate = stock_dict['RevenueGrowthRate5Years']
        stock_cashpershare = stock_dict['CashPerShareYear']
        stock_debt2equity = stock_dict['TotalDebtToEquityYear'].replace(",","")
        stock_ldebt2equity = stock_dict['LTDebtToEquityYear'].replace(",","")
        stock_debt2asset = stock_dict['TotalDebtToAssetsYear']
        stock_earning_yield = 0
        stock_bps_yield = 0
        stock_cash_yield = 0
        if Decimal(stock_price) != 0:
            # 收益率 eps / price
            stock_earning_yield = fpformat.fix((float(stock_eps) / float(stock_price)),4)
            # 净资产比率  bps / price
            stock_bps_yield = fpformat.fix((float(stock_bps) / float(stock_price)),4)
            #stock_bps_yield = stock_dps
            # 现金流价格比率
            stock_cash_yield = fpformat.fix((float(stock_cashpershare) / float(stock_price)),4)


        sql_cmd = 'insert into stock values(NULL,"%s","%s","%s",%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"%s")' % (stock_exchange,stock_title,stock_symbol,stock_price,stock_50_avg,stock_200_avg,stock_volume,stock_avg_volume,stock_eps,stock_bps,stock_dps,stock_roi_ttm,stock_earning_yield,stock_bps_yield,stock_cashpershare,stock_cash_yield,stock_debt2equity,stock_ldebt2equity,stock_debt2asset,note)
        try:
            db_cursor.execute(sql_cmd)
            cx.commit()
        except Exception,e:
            print "sql_cmd = " + sql_cmd
            print "%s : Error = %s" % (stock_symbol,e)
            sys.exit()



def stock_filter(stock_dict):
    """ filter stock data by condition """
    p50day_moving_avg = stock_dict['Price50DayAverage']
    p200day_moving_avg = stock_dict['Price200DayAverage']
    price = stock_dict['QuoteLast']
    earnings_per_share = stock_dict['EPS']
    cash_per_share = stock_dict['CashPerShareYear']
    bookval = stock_dict['BookValuePerShareYear']
    is_over_200_5_percent = False    #当前价格在200天均线值的 +5% 之内
    is_over_200 = False    #当前价格在200天上
    is_over_50 = False     #当前价格在50天均线上 
    is_cash = False  # 高现金流,可能低估
    is_eps_over_bond = False    # 收益率大于债券收益率
    output_str = None
    is_cash = ""
    is_bond = None
    is_low_200 = False

    #if float(p200day_moving_avg) <= float(price) <= float(p200day_moving_avg) * 1.05 : is_over_200_5_percent = True 
    if float(p50day_moving_avg) <= float(price): is_over_50 = True
    #if float(p200day_moving_avg) <= float(p50day_moving_avg) <= float(p200day_moving_avg) * 1.05: is_over_200_5_percent = True
    #if float(p200day_moving_avg) >= float(p50day_moving_avg) >= float(p200day_moving_avg) * 0.95: is_over_200_5_percent = True
    if (float(earnings_per_share) / 0.06) >= float(price): 
        is_bond = "over bond"
        is_eps_over_bond = True
    if float(p200day_moving_avg) <= float(price) : is_over_200 = True 
    if float(p200day_moving_avg) >= float(price) : is_low_200 = True 
    if (Decimal(cash_per_share) / Decimal(price)) >= Decimal("0.4")  : is_cash = "over cash 40%" # 高现金流,可能低估

    #if not is_over_200: return False 
    #if is_bond == "": return False
    #if (is_over_200 or is_over_50):
    #if is_over_200 and is_eps_over_bond:
    if True:
        over_200 = ""
        over_50 = ""
        #if is_over_200_5_percent: over_200 = "50SMA_200SMA_%5"
        if is_over_200: over_200 = "OVER_200_SMA"
        if is_over_50: over_50 = "OVER_50_SMA"
        #if is_eps_over_bond and (is_over_200_5_percent or is_over_200):
        #if is_over_200:
        #    output_str = "%s %s %s" % (over_200,is_cash,is_bond)
        #    return output_str
        #else:
        #    return False
        #output_str = "%s %s %s" % (over_200,is_cash,is_bond)
        output_str = "%s %s %s %s" % (over_200,over_50,is_cash,is_bond)
        if not output_str: output_str = "Empty"
        return output_str
    else:
        return False


def sort_stock(result_list,monitor_data):
    """ 按每个指标,取排名前50,然后去掉重复数据 """
    sorted_data = []
    # 按照股息收益率排序 dps_yield
    sorted_list = sorted(result_list, key=lambda result: Decimal(result[2]),reverse=True)
    count = 0
    for data in sorted_list:
        #if count == 50 : break
        (exchange,symbol,dps_yield,stock_bps_yield,cash_yield,debt2asset,stock_earning_yield,stock_roi_ttm,top_order) = data
        #print "symbol = %s,dps_yield = %s" % (symbol,dps_yield)
        #sorted_data.append(data)
        count = count + 1

    # 按照净资产价格比率排序 stock_bps_yield
    sorted_list = sorted(result_list, key=lambda result: Decimal(result[3]),reverse=True)
    count = 0
    for data in sorted_list:
        #if count == 50 : break
        #(exchange,symbol,dps_yield,stock_bps_yield,cash_yield,debt2asset,stock_earning_yield,stock_roi_ttm,top_order) = data
        #print "symbol = %s,stock_bps_yield = %s" % (symbol,stock_bps_yield)
        sorted_data.append(data)
        count = count + 1

    # 按照现金价格比率排序 cash_yield
    sorted_list = sorted(result_list, key=lambda result: Decimal(result[4]),reverse=True)
    count = 0
    for data in sorted_list:
        #if count == 50 : break
        #(exchange,symbol,dps_yield,stock_bps_yield,cash_yield,debt2asset,stock_earning_yield,stock_roi_ttm,top_order) = data
        #print "symbol = %s,cash_yield = %s" % (symbol,cash_yield)
        sorted_data.append(data)
        count = count + 1

    # 按照资产负债率排序 debt2asset
    sorted_list = sorted(result_list, key=lambda result: Decimal(result[5]))
    count = 0
    for data in sorted_list:
        #if count == 50 : break
        #(exchange,symbol,dps_yield,stock_bps_yield,cash_yield,debt2asset,stock_earning_yield,stock_roi_ttm,top_order) = data
        #print "symbol = %s,debt2asset = %s" % (symbol,debt2asset)
        sorted_data.append(data)
        count = count + 1

    # 按照收益率排序 stock_earning_yield
    sorted_list = sorted(result_list, key=lambda result: Decimal(result[6]),reverse=True)
    count = 0
    for data in sorted_list:
        #if count == 50 : break
        #(exchange,symbol,dps_yield,stock_bps_yield,cash_yield,debt2asset,stock_earning_yield,stock_roi_ttm,top_order) = data
        #print "symbol = %s,stock_earning_yield = %s" % (symbol,stock_earning_yield)
        sorted_data.append(data)
        count = count + 1

    # 按照投资回报率排序 stock_roi_ttm
    sorted_list = sorted(result_list, key=lambda result: Decimal(result[7]),reverse=True)
    count = 0
    for data in sorted_list:
        #if count == 50 : break
        #(exchange,symbol,dps_yield,stock_bps_yield,cash_yield,debt2asset,stock_earning_yield,stock_roi_ttm,top_order) = data
        #print "symbol = %s,stock_roi_ttm = %s" % (symbol,stock_roi_ttm)
        sorted_data.append(data)
        count = count + 1

    # 按照综合排名排序 top_order
    sorted_list = sorted(result_list, key=lambda result: Decimal(result[8]))
    count = 0
    for data in sorted_list:
        #if count == 100 : break
        #(exchange,symbol,dps_yield,stock_bps_yield,cash_yield,debt2asset,stock_earning_yield,stock_roi_ttm,top_order) = data
        #print "symbol = %s,top_order = %s" % (symbol,top_order)
        sorted_data.append(data)
        count = count + 1

    # 去除重复数据
    #print "before len = %s" % len(sorted_data)
    sorted_data = set(sorted_data)
    #print "after len = %s" % len(sorted_data)
    # 持久化dict,用来cache文章修改时间
    fout = open(monitor_data, "w")
    pickle.dump(sorted_data, fout, protocol=0)
    fout.close()


def main():
    """ main function """
    base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    cache_dir = "%s/tmp" % (base_dir)
    db_file = "%s/db/filter_db" % (base_dir)
    monitor_data = "%s/monitor_data" % (cache_dir)
    cache_file = "%s/%s" % (cache_dir,"google_json")
    (db_cursor,cx) = connect_db(db_file)
    cx.text_factory=str

    stock_data_list = request(cache_file)
    update_db(db_cursor,cx,analyse_stock(stock_data_list))

    #update_db(db_cursor,cx,analyse_stock(cache_file))
    # define rank dict
    ey_dict = {}    # 收益率
    roi_dict = {}   # 投资回报率
    bps_dict = {}   # 净资产/价格比率

    # sort 
    eps_yield_sql = "select (select COUNT(0) from stock t1 where t1.stock_earning_yield > t2.stock_earning_yield) as 'RowNum',stock_symbol from stock t2 order by stock_earning_yield DESC"
    db_cursor.execute(eps_yield_sql)
    rs = db_cursor.fetchall()
    for item in rs:
        (eps_rank,stock_symbol)  = item
        ey_dict[stock_symbol] = eps_rank

    roi_sql = "select (select COUNT(0) from stock t1 where t1.stock_roi_ttm > t2.stock_roi_ttm) as 'RowNum',stock_symbol from stock t2 order by stock_roi_ttm DESC"
    db_cursor.execute(roi_sql)
    rs = db_cursor.fetchall()
    for item in rs:
        (roi_rank,stock_symbol)  = item
        roi_dict[stock_symbol] = roi_rank

    # output
    result_data = []
    print "交易所\t代码\t价格\t股息收益率\t净资产价格比\t收益率\t投资回报率\t每股现金\t每股现金比率\t总负债权益比\t长期负债权益比\t资产负债\t综合排名\t状态"
    sql = "select exchange_name,stock_symbol,stock_price,stock_dps,stock_bps_yield,stock_earning_yield,stock_roi_ttm,stock_cashpershare,stock_cash_yield,stock_debt2equity,stock_ldebt2equity,stock_debt2asset,stock_note from stock"
    db_cursor.execute(sql)
    rs = db_cursor.fetchall()
    for item in rs:
        (exchange,symbol,price,stock_dps,stock_bps_yield,stock_earning_yield,stock_roi_ttm,cash_pershare,cash_yield,debt2equity,ldebt2equity,debt2asset,note) = item
        try:
            print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (exchange,symbol,price,stock_dps,stock_bps_yield,stock_earning_yield,stock_roi_ttm,cash_pershare,cash_yield,debt2equity,ldebt2equity,debt2asset,ey_dict[symbol]+roi_dict[symbol],note)
            # data field : 交易所,代码,股息收益率,净资产价格比率,现金价格比率,资产负债率,收益率,投资回报率,综合排名
            tmp_str = "%s,%s,%s,%s,%s,%s,%s,%s,%s" % (exchange,symbol,stock_dps,stock_bps_yield,cash_yield,debt2asset,stock_earning_yield,stock_roi_ttm,ey_dict[symbol]+roi_dict[symbol])
            data = tuple(tmp_str.split(","))            
            result_data.append(data)
        except Exception,e:
            print "%s : Error = %s" % (symbol,e)    
    cx.close()
    # 调用指标排序函数
    sort_stock(result_data,monitor_data)

if __name__ == "__main__":
    main()




