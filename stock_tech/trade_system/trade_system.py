#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import yaml
import sys
import getopt
import commands
#import pysqlite2.dbapi2 as sqlite
import sqlite3 as sqlite
import datetime
from pprint import pprint

def load_config():
    """
    读取配置文件
    """
    configFile = "%s/conf/%s" % (base_dir,"global.yaml")
    stream = file(configFile, 'r')   
    data = yaml.load(stream)
    return data

def connect_db():
    """
    股票持仓数据库(portfolio)  
    symbol      股票代码 
    trade_date  交易日期
    action      buy/sell
    quantity    数量
    open_price  开仓价格
    stop_price  止损价格
    gain_price  预期止盈价格
    Comm        手续费/佣金
    is_close    是否平仓

    资金数据库(money)
    free_money      当前可用资金(开仓可用资金) 刚开始为初始资金
    balance_date    结算日(每次交易或者每周日  结算一次一条记录)
    """
    db_file = "%s/db/%s" % (base_dir,"portfolio_db")
    if os.path.isfile(db_file):
        cx = sqlite.connect(db_file)
        cu = cx.cursor()
        return (cu,cx)
    else:
        cx = sqlite.connect(db_file)
        cu = cx.cursor()
        # 投资组合表
        cu.execute('''
            create table portfolio(
            id integer primary key,
            symbol varchar(20),
            trade_date varchar(50),
            action varchar(10),
            quantity varchar(10),
            open_price  varchar(20),
            stop_price  varchar(20),
            gain_price  varchar(20),
            comm   varchar(20),
            is_close  varchar(20) DEFAULT 'no'
            )''')
        cu.execute('''
            create table money(
            balance_date varchar(20) primary key,
            free_money varchar(20)
            )''')

        return (cu,cx)

def update_db(trade_data,action):
    """ 插入持仓数据 """
    (db_cursor,cx) = connect_db()
    symbol = trade_data['symbol']
    trade_date = trade_data['trade_date']
    action = trade_data['action']
    quantity = trade_data['quantity']
    open_price = trade_data['open_price']
    stop_price = trade_data['stop_price']
    gain_price = trade_data['gain_price']
    comm = trade_data['comm']
    sql_cmd = 'insert into portfolio values(NULL,"%s","%s","%s","%s","%s","%s","%s","%s","no")' % (symbol,trade_date,action,quantity,open_price,stop_price,gain_price,comm)
    db_cursor.execute(sql_cmd)
    cx.commit()
    # 更新is_close 平仓标识
    if action.lower() == "close":
        sql_cmd = "update portfolio set is_close = 'yes' where id=%s" % (trade_data['stock_id'])
        db_cursor.execute(sql_cmd)
        cx.commit()
    cx.close()
    # 平仓
    if action.lower() == "close":
        trade_val = trade_data['gain_money']
    # 计算本次交易使用的资金(不管是作多还是做空都是从资金中扣除)
    else:
        trade_val = float(open_price) * float(quantity) + float(comm)
    return trade_val

def trade_update_cash(trade_val,action="open"):
    """
    买入或者卖出关联现金帐户(买入减少现金，卖出增加现金)
    """
    # 取得当前最后现金
    (db_cursor,cx) = connect_db()
    sql_cmd ="select free_money from money order by balance_date desc limit 1"
    db_cursor.execute(sql_cmd)
    rs = db_cursor.fetchone()
    current_free_money = rs[0]
    # 不管作多还是做空都是从资中扣除
    if action.lower() == "close":
        new_free_money = float(current_free_money) + trade_val
    else:
        new_free_money = float(current_free_money) - trade_val
    cx.close()
    # 
    #更新现金表
    update_cash(new_free_money) 


    
def update_cash(cash_val):
    """
    更新初始现金数据
    """
    (db_cursor,cx) = connect_db()
    try:
        sql_cmd = "insert into money values(date('now'),'%s')" % (cash_val)
        db_cursor.execute(sql_cmd)
    except sqlite.IntegrityError,e:
        sql_cmd = "update money set free_money = '%s' where balance_date=date('now')" % (cash_val)
        db_cursor.execute(sql_cmd)
    except Exception as inst:
        print "exception type = %s,Error = %s" % (type(inst),inst)

    cx.commit()
    cx.close()

def stop_atr(symbol,open_price,action):
    """
    2倍ATR止损,自动计算
    """
    symbol= symbol.upper()
    atr_val = get_atr_output(symbol)
    per_stock_loss =  1*float(atr_val)
    per_stock_gain =  3*float(atr_val)
    if action.lower() == "buy":
        stop_price = float(open_price) - per_stock_loss 
        gain_price = float(open_price) + per_stock_gain
    elif action.lower() == "sell":
        stop_price = float(open_price) + per_stock_loss 
        gain_price = float(open_price) - per_stock_gain
    return (per_stock_loss,stop_price,gain_price)

def get_atr_output(symbol,timeframe='day'):
    """
    """
    symbol = symbol.upper()
    ##if DEBUG: print "DEBUG : CURRENT pROCESS SYMBOL=%s" % symbol
    #print "DEBUG : CURRENT pROCESS SYMBOL=%s" % symbol
    if timeframe == 'day':
        cmd = "cd /home/hua.fu/geniustrader/Scripts;./display_indicator.pl  --last-record --timeframe=%s \
                --tight I:ATR %s|grep -P '\[\d+-\d+\-\d+]*.*'" % (timeframe,symbol)

    if timeframe == 'week':
        cmd = "cd /home/hua.fu/geniustrader/Scripts;./display_indicator.pl  --last-record --timeframe=%s \
                --tight I:ATR %s|grep -P '\[\d+-\d+]*.*'" % (timeframe,symbol)

    if timeframe == 'month':
        cmd = "cd /home/hua.fu/geniustrader/Scripts;./display_indicator.pl  --last-record --timeframe=%s \
                --tight I:ATR %s| grep -P '\[\d+\/\d+]*.*'" % (timeframe,symbol)

    #print "DEBUG indicator_cmd = %s" % cmd
    (status,output) = commands.getstatusoutput(cmd)
    if status != 0:
        return False
    base_point =  output.split("=")[1].strip()
    return base_point

def auto_order(stock_symbol,open_price,stop_price,all_loss_money,commision,action,stock_num):
    """
    根据atr自动计算止损，止盈，订单
    """
    trade_data = {}
    stock_symbol = stock_symbol.upper()
    (per_stock_loss,stop_price_atr,gain_price) = stop_atr(stock_symbol,open_price,action)
    if action.lower() =="buy":
        buy_tag = "Buy"
        sell_tag = "Sell"
    elif action.lower() =="sell":
        buy_tag = "Sell"
        sell_tag = "Buy"

    if stop_price:
        per_stock_loss = abs(float(open_price) - float(stop_price))
    else:
        stop_price = stop_price_atr

    comm_money =  commision * float(stock_num)
    stock_loss_money = per_stock_loss * float(stock_num) + comm_money 
    if stock_loss_money > all_loss_money:
        print " Warning : stock stop  money > global loss money ,please attention !!!"
    gain_money = abs(gain_price - float(open_price)) * float(stock_num) - comm_money


    trade_data['symbol'] = stock_symbol
    #trade_data['trade_date'] = "2012-07-01"
    #trade_data['action'] = "buy"
    trade_data['quantity'] = stock_num
    trade_data['open_price'] = open_price
    trade_data['stop_price'] = stop_price
    trade_data['gain_price'] = gain_price
    trade_data['comm'] = comm_money 
    sell_stop_tag  = "%s Stop" % (sell_tag)
    print "%-10s\t%-15s\t%-15s\t%-10s" % ("Symbol","Action.","Price","Num")
    print "=" * 60
    print "%-10s\t%-15s\t%-15s\t%-10s" % (stock_symbol,buy_tag,open_price,stock_num)
    print "%-10s\t%-15s\t%-15s\t%-10s" % (stock_symbol,sell_tag,gain_price,stock_num)
    print "%-10s\t%-15s\t%-15s\t%-10s" % (stock_symbol,sell_stop_tag,stop_price,stock_num)
    print "+" * 60
    print "gain_money=%s\tloss_money=%s" % (gain_money,stock_loss_money)
    print "\n"
    return trade_data

def show_stock_list():
    """ 显示目前持有的股票，然后选择平仓 """
    # 输出股票代码等信息
    (db_cursor,cx) = connect_db()
    sql = "select * from  portfolio where is_close='no' and action!='close'"
    db_cursor.execute(sql)
    rs = db_cursor.fetchall()
    if len(rs) == 0:
        print "No stock to close ,exit"
        sys.exit()
    print "%-5s\t%-10s\t%-8s\t%-10s\t%-5s" % ("No.","Symbol","OpenPrice","Action","Num")
    print "=" * 65
    index  = len(rs) 
    for item  in rs:
        trade_id = item[0]
        symbol = item[1]
        trade_date = item[2]
        action = item[3]
        stock_num = item[4]
        open_price = item[5]
        print "%-5s\t%-10s\t%-8s\t%-10s\t%-5s" % (trade_id,symbol,open_price,action,stock_num)
    #print "%2s)\t%s" % (index+1,"Restart ........")
    user_input = None
    while(True):
        user_input =  raw_input("\nPlease Choice Stock Id : ")
        if not user_input : continue
        #elif user_input.isdigit() and 1 <= int(user_input) <= index:
        elif user_input.isdigit() :
            break
    stock_id = user_input
    cx.close()
    return stock_id

def close_order(stock_id,commision,trade_date):
    """
    平仓
    """
    (db_cursor,cx) = connect_db()
    sql = "select * from  portfolio where id=%s" % (stock_id)
    db_cursor.execute(sql)
    rs = db_cursor.fetchone()
    trade_id = rs[0]
    symbol = rs[1]
    #trade_date = rs[2]
    action = rs[3]
    stock_num = rs[4]
    open_price = rs[5]
    cx.close() 
    trade_data = {}
    symbol = symbol.upper()
    user_input = None
    while(True):
        user_input =  raw_input("\nPlease Input Close Price: ")
        if not user_input : continue
        #elif user_input.isdigit():
        break
    close_price = user_input

    #if action.lower() =="buy":      # 卖出,得到现金
    #    per_stock_gain = float(close_price) - float(open_price) - float(commision)
    #elif action.lower() =="sell":   # 买回,减少现金
    #    per_stock_gain = float(open_price) - float(close_price) - float(commision)
    per_stock_gain = abs(float(close_price) - float(open_price))
    comm_money = float(commision) * float(stock_num)
    #gain_money = float(per_stock_gain) * float(stock_num) - comm_money 
    if action.lower()=="buy":        # 作多平仓
        gain_money = float(close_price) * float(stock_num) - comm_money
    else:                           # 做空平仓
        gain_money = (float(open_price) + per_stock_gain) * float(stock_num) - comm_money

    trade_data['symbol'] = symbol
    trade_data['trade_date'] = trade_date
    trade_data['action'] = "close"
    trade_data['quantity'] = stock_num
    trade_data['open_price'] = open_price
    trade_data['stop_price'] = ""
    trade_data['gain_price'] = close_price
    trade_data['gain_money'] = gain_money
    trade_data['stock_id'] = stock_id 
    trade_data['comm'] = comm_money 
    print "\n%-5s\t%-8s\t%-8s\t%-5s\t%-5s" % ("Symbol","OpenPrice","ClosePrice","Num","GainMoney")
    print "=" * 65
    print "%-5s\t%-8s\t%-8s\t%-5s\t%-5s" % (symbol,open_price,close_price,stock_num,gain_money)
    print "+" * 65
    user_input = raw_input("update trade db , Are you sure [Y/y]:")
    if user_input.lower() == "y":
        trade_val = update_db(trade_data,"close")
        trade_update_cash(trade_val,"close")



def usage():
    print '''
Usage: trade_system.py.py [options...]
Options: 
    -o/--open_price                     : buy/sell price
    -s/--stop_price                     : stop lost price
    -c/--symbol_code                    : stock symbol
    -n/--stock_num                      : buy or sell number
    -t/--trade_date                     : trade date [format: 2010-07-01]
    -a/--action                         : buy or sell or close(平仓)
    -D/--Deposit                        : setting init money(输入初始现金)
    -d/--debug                          : run in debug mode 
    -h/--help                           : this help info page
    
Example:
    # default is checking all stock which in monitor db
    trade_system.py.py -o 10 -s 9.5 
    '''

def main():
    """ main function """
    global base_dir,DEBUG 
    DEBUG = False
    base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

    #base_dir = /home/hua.fu/geniustrader
    cache_dir = "%s/tmp" % (base_dir)
    stock_db = "%s/db/stock_db" % (base_dir)
   
    try:
        opts, args = getopt.getopt(sys.argv[1:],'dho:s:c:n:t:a:D:')
    except getopt.GetoptError:
        usage()
        sys.exit()
    
    #各个变量保存
    open_price = None         #开仓价格
    stop_price = None       #止损价格
    stock_symbol = None
    stock_num = 200
    trade_date = datetime.datetime.now().strftime("%Y-%m-%d")
    action = "buy"
    init_cash = None
    
    for opt, arg in opts: 
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt == '-s':
            stop_price = arg
        elif opt == '-o':
            open_price = arg
        elif opt == '-c':
            stock_symbol = arg
        elif opt == '-n':
            stock_num = arg
        elif opt == '-t':
            trade_date = arg
        elif opt == '-a':
            action = arg
        elif opt == '-D':
            init_cash = arg
        elif opt == '-d':
            DEBUG = True
              
    # 读取配置
    trade_config = load_config() 
    #pprint(trade_config)
    stop_loss = trade_config['stop_loss']
    stop_gain = trade_config['stock_stop_gain']
    all_money = trade_config['int_all_money']
    commision = trade_config['commision']

    if init_cash:
        update_cash(init_cash)
        print "Setting Init Cash Complete"
        sys.exit()

    if action.lower() == "close":
        stock_id = show_stock_list()
        close_order(stock_id,commision,trade_date)
        sys.exit()

    if  not  open_price:
        usage()
        sys.exit()

    # 总资金的2%止损
    loss_money = float(all_money) * float(stop_loss) 
    #if stock_num:
    #    trade_data = auto_order(stock_symbol,open_price,stop_price,loss_money,commision,stock_num)
    #else:
    #    trade_data = auto_order(stock_symbol,open_price,stop_price,loss_money,commision)
    trade_data = auto_order(stock_symbol,open_price,stop_price,loss_money,commision,action,stock_num)

    trade_data['trade_date'] = trade_date
    trade_data['action'] = action
    pprint(trade_data)
    user_input = raw_input("update trade db , Are you sure [Y/y]:")
    if user_input.lower() == "y":
        trade_val = update_db(trade_data,action)
        trade_update_cash(trade_val)

if __name__ == "__main__":
    main()

