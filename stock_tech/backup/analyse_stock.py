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
        return (cu,cx)
    else:
        #create
        cx = sqlite.connect(db_file)
        cu = cx.cursor()
        cu.execute('''create table stock(
            id integer primary key,
            market_name varchar(20),
            stock_name varchar(50),
            stock_code varchar(20),
            category varchar(50) DEFAULT NULL,
            country varchar(50) DEFAULT NULL
            )''')
        return (cu,cx)

def usage():
    print '''
Usage: analyse_stock.py [options...]
Options: 
    -e : Exchange Name 
    -c : User-Defined Category Name
    -f : Read stock info from file and save to db
    -d : delete from db by stock code
    -n : stock name
    -s : stock code
    -a : check all stock
    -t : count info
    -z : country info
    -h : this help info
    analyse_stock.py -s ras -n "RAIT Financial Trust" 
    '''

try:
    opts, args = getopt.getopt(sys.argv[1:],'htae:c:f:dn:s:z:')
except getopt.GetoptError:
    usage()
    sys.exit()
if len(opts) == 0:
    usage()
    sys.exit()

# 定义变量 
base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
cache_dir = "%s/cache" % (base_dir)
db_file = "%s/stock_db" % (base_dir)

stock_name = ""
stock_code = ""
stock_file = ""
stock_category = ""
stock_exchange = ""
stock_country = ""
is_del_stock = False    
is_check_all = False
is_count = False    # 统计

for opt, arg in opts: 
    if opt in ('-h', '--help'):
        usage()
        sys.exit()
    elif opt == '-d':
        is_del_stock = True
    elif opt == '-a':
        is_check_all = True
    elif opt == '-t':
        is_count = True
    elif opt == '-f':
        stock_file = arg
    elif opt == '-c':
        stock_category = arg
    elif opt == '-e':
        stock_exchange = arg
    elif opt == '-s':
        stock_code =  arg
    elif opt == '-n':
        stock_name = arg
    elif opt == '-z':
        stock_country = arg

(db_cursor,cx) = connect_db(db_file)
cx.text_factory=str

# del stock from db
if stock_code and is_del_stock:
    sql_cmd='delete from  stock where stock_code = "%s"' % (stock_code)
    db_cursor.execute(sql_cmd)
    cx.commit()
    sys.exit()

if stock_code:
    cache_file = "%s/%s" % (cache_dir,stock_code)
    stock_exchange = analyse_stock(cache_file,stock_code,stock_name)
    if stock_exchange != "pass" and stock_exchange != "del":
        stock_exchange = stock_exchange.replace('"','')
        # 判断是否已经插入数据库中
        sql_cmd = "select count(*) from stock where market_name ='%s' and stock_code = '%s'" % (stock_exchange,stock_code)
        db_cursor.execute(sql_cmd)
        rs = db_cursor.fetchone()
        rs_count = rs[0]
        if not rs_count:
            sql_cmd = 'insert into stock values(NULL,"%s","%s","%s","%s","%s")' % (stock_exchange,stock_name,stock_code,stock_category,stock_country)
            db_cursor.execute(sql_cmd)
            cx.commit()
        elif stock_name:
            sql_cmd = 'update stock set stock_name="%s",country="%s"  where market_name ="%s" and stock_code = "%s"' % (stock_name,stock_country,stock_exchange,stock_code)
            db_cursor.execute(sql_cmd)
            cx.commit()
    elif stock_exchange == "del":
        sql_cmd='delete from  stock where stock_code = "%s"' % (stock_code)
        db_cursor.execute(sql_cmd)
        cx.commit()
    sys.exit()
    
# 遍历检查 
index_1 = {}  # PE 指标
index_2 = {}  # EPS 指标
index_3 = {}  # 其他指标

sort_index = {} # 各指标总排序结果
result_index = {} # 最总排序结果
sql_cmd =""
if is_check_all:
    if stock_exchange:
        sql_cmd = 'select * from stock where market_name="%s" order by market_name' % (stock_exchange)
    elif stock_country:
        sql_cmd = 'select * from stock where country="%s" order by market_name' % (stock_country)
    else:
        sql_cmd = 'select * from stock order by market_name'
    db_cursor.execute(sql_cmd)
    rs = db_cursor.fetchall()
    for item in rs:
        (stock_id,market_name,stock_name,stock_code,stock_category,stock_country)  = item
        cache_file = "%s/%s" % (cache_dir,stock_code)
        is_update = False 
        #if int(time.time()) - int(os.stat(cache_file).st_mtime) >= 86400: is_update = True
        #print "stock_code = %s ==================" % stock_code
        if analyse_stock(cache_file,stock_code,stock_name,is_update) == "del" and not market_name:
            sql_cmd='delete from  stock where stock_code = "%s"' % (stock_code)
            db_cursor.execute(sql_cmd)
            cx.commit()

# 对指标进行排序
sort_pe = sorted(index_1.items(),key=itemgetter(1))
count = 1
for item in sort_pe:
    (sy,pe_val) =  item
    key = "%s_%s" % (sy,"pe-order")
    sort_index[key] = count
    count = count + 1
    #print "symbol = %s PE = %s" % (sy,pe_val) 

sort_eps= sorted(index_2.items(),key=itemgetter(1),reverse=True)
count = 1
for item in sort_eps:
    (sy,eps_val) = item
    key = "%s_%s" % (sy,"eps-order")
    sort_index[key] = count
    count = count + 1
    #print "symbol = %s EPS = %s" % (sy,eps_val) 

#sys.exit()
print "symbol\tpe-order\teps-order\ttop-order\tnote"
for sy in index_1.keys():
    pekey  = "%s_%s" % (sy,"pe-order")
    epskey = "%s_%s" % (sy,"eps-order")
    result = "%s\t%s\t%s\t%s\t%s" % (sy,sort_index[pekey],sort_index[epskey],sort_index[pekey]+sort_index[epskey],index_3[sy])
    print result
#print result_index
# 分组统计
if is_count:
    db_cursor.execute('select market_name,country,count(*) as num from stock group by market_name')
    rs = db_cursor.fetchall()
    print "Stock_Exchange\tStock_Count\tCountry"
    for item in rs:
        (market_name,stock_country,stock_count)  = item
        print "%8s\t%4s\t%4s" % (market_name,stock_count,stock_country)

