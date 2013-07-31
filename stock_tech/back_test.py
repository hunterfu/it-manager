#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = 0.1

import urllib,urllib2,sys
from pprint import pprint
from sys import argv
import os
import commands

symbol = None
try:
    symbol = argv[1]
    symbol = symbol.upper()
except Exception,e:
    pass

base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
report_tpl = "%s/report_backtest" % (base_dir)

## === 图形模式测试  ====#
#buy_signal = """ { Signals::Generic::And \
#{ S:Generic:Repeated {S:Generic:Increase {I:SMA 200} } 60 } \
#{ S:Generic:Above {I:Prices CLOSE} {I:SMA 200 {I:Prices CLOSE} } } \
#{ Signals::Generic::Or \
# {I:Generic:PeriodAgo 1 { S:Generic:Repeated {S:Generic:Below {I:STO/4} 25} 3 }} \
# {I:Generic:PeriodAgo 1 { S:Generic:Repeated {S:Generic:Below {I:STO/4} 25} 4 }} \
# {I:Generic:PeriodAgo 1 { S:Generic:Repeated {S:Generic:Below {I:STO/4} 25} 5 }} \
# {I:Generic:PeriodAgo 1 { S:Generic:Repeated {S:Generic:Below {I:STO/4} 25} 6 }} \
#}\
#{ S:Generic:Below {I:RSI} 60 } { S:Generic:Above {I:STO/1} 20 } { S:Generic:Above {I:RSI} 30 } }\
#{S:Generic:False } """

# back test command
# for ibm perfect
#buy_signal = """ { S:Generic:And \
#{ S:Generic:Repeated {S:Generic:Increase {I:SMA 200} } 30 }\
#{ S:Generic:Repeated {S:Generic:Above {I:SMA 50} {I:SMA 200} } 20} \
#{ S:Generic:Above {I:Prices CLOSE} {I:SMA 200 {I:Prices CLOSE} } } \
#{ S:Generic:Increase {I:SMA 5 {I:MFI}} } \
#{ S:Generic:Increase {I:MACD/3} } \
#{ S:Generic:Above {I:MFI} 25 } \
#{ S:Generic:Above {I:ADX} 30 } \
#{ S:Generic:CrossOverUp {I:STO/4} 25 } } {S:Generic:False } """

#buy_signal = """ { S:Generic:And \
#{ S:Generic:Repeated {S:Generic:Increase {I:SMA 200} } 30 }\
#{ S:Generic:Repeated {S:Generic:Above {I:SMA 50} {I:SMA 200} } 20} \
#{ S:Generic:Above {I:Prices CLOSE} {I:SMA 200 {I:Prices CLOSE} } } \
#{ S:Generic:Above {I:MFI} 25 } \
#{ Signals::Generic::Or \
# {I:Generic:PeriodAgo 1 { S:Generic:Repeated {S:Generic:Below {I:STO/4} 25} 4 }} \
# {I:Generic:PeriodAgo 1 { S:Generic:Repeated {S:Generic:Below {I:STO/4} 25} 5 }} \
# {I:Generic:PeriodAgo 1 { S:Generic:Repeated {S:Generic:Below {I:STO/4} 25} 6 }} \
#}\
#{ S:Generic:CrossOverUp {I:STO/4} 25 } } {S:Generic:False } """

#buy_signal = """ {S:Generic:And \
#{ S:Generic:Above {I:MFI} 25 } \
#{ Signals::Generic::Or \
# {I:Generic:PeriodAgo 1 { S:Generic:Repeated {S:Generic:Below {I:STO/4} 25} 4 }} \
# {I:Generic:PeriodAgo 1 { S:Generic:Repeated {S:Generic:Below {I:STO/4} 25} 5 }} \
# {I:Generic:PeriodAgo 1 { S:Generic:Repeated {S:Generic:Below {I:STO/4} 25} 6 }} \
#}\
#{ S:Generic:CrossOverUp {I:STO/4} 25 }  } {S:Generic:False } """


#buy_signal = """ {S:Generic:And \
#{ S:Generic:Repeated {S:Generic:Increase {I:SMA 200} } 30 } \
#{ S:Generic:Repeated {S:Generic:Increase {I:SMA 50} } 5} \
#{ S:Generic:Repeated {S:Generic:Increase {I:SMA 20} } 10} \
#{ S:Generic:Repeated {S:Generic:Above {I:SMA 20} {I:SMA 50} } 5} \
#{ S:Generic:Repeated {S:Generic:Above {I:SMA 50} {I:SMA 200} } 10} \
#{ S:Generic:Above {I:Prices CLOSE} {I:SMA 200 {I:Prices CLOSE} } } \
#{ S:Generic:Equal {I:Generic:MinInPeriod 2 {I:STO/4}}  {I:Generic:MinInPeriod 10{I:STO/4}} } } {S:Generic:False } """

#buy_signal = """ { S:Generic:And \
#{ S:Generic:Repeated {S:Generic:Increase {I:SMA 200} } 30 }\
#{ S:Generic:Increase {I:SMA 10 { I:Generic:Eval  {I:SMA 50} - {I:SMA 200} }}} \
#{ S:Generic:Repeated {S:Generic:Above {I:SMA 50} {I:SMA 200} } 20} \
#{ S:Generic:Above {I:Prices CLOSE} {I:SMA 200 {I:Prices CLOSE} } } \
#{ S:Generic:CrossOverUp {I:STO/4} 20 } } {S:Generic:False } """

#buy_signal = """ { S:Generic:And \
#{ S:Generic:Repeated {S:Generic:Increase {I:SMA 200} } 20 }\
#{ S:Generic:Repeated {S:Generic:Above {I:SMA 50} {I:SMA 200} } 20} \
#{ S:Generic:Above {I:Prices CLOSE} {I:SMA 200 {I:Prices CLOSE} } } \
#{ S:Generic:CrossOverUp {I:STO/4} 20 } } {S:Generic:False } """

# ====== 新模式2测试  =============#
#buy_signal = """ { S:Generic:And \
#{ S:Generic:Repeated {S:Generic:Above { I:SMA 50 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} }\
#        { I:Generic:PeriodAgo 5 { I:SMA 50 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}}}}} 10 }
#{S:Generic:CrossOverUp {I:STO/1} 25}\
#{ S:Generic:Above {I:MACD/3} 0 }\
#} {S:Generic:False } """

#{ S:Generic:Repeated {S:Generic:Increase { I:SMA 50 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} }} 20 } \
# ====== 新模式1测试  =============#
#buy_signal = """ { S:Generic:And \
#{ S:Generic:Above {I:MACD/3} 0 }\
#{ I:Generic:PeriodAgo 1 { S:Generic:Repeated { S:Generic:Below {I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } \
#{ I:SMA 50 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } 50}}\
#{ S:Generic:CrossOverUp {I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } { I:SMA 50 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } \
#} {S:Generic:False } """

#{ S:Generic:Repeated {S:Generic:Increase { I:SMA 50 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} }} 20 } \
#{ S:Generic:Increase {I:ADX} } \
#{ S:Generic:Repeated { S:Generic:Above {I:SMA 5 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } \
#{ I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } 5}\
#{ S:Generic:Repeated { S:Generic:Above {I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } \
#{ I:SMA 50 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } 4}\
#{ S:Generic:Increase {I:SMA 50 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}}}  } \
#{ S:Generic:Repeated { S:Generic:Above {I:SMA 5 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } \
#{ I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } 5}\
#{ S:Generic:Above {I:ADX}  30}\
#{ S:Generic:Above {I:Generic:Eval {I:SMA 5 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}}} - \
#{ I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } {I:Generic:Eval 0.5*{I:ATR 40}} } \
#{ S:Generic:Above {I:SMA 5 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } { I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } \
#{ S:Generic:Above {I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } { I:SMA 25 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } \
#{ S:Generic:Repeated { S:Generic:Above {I:SMA 5 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } \
#{ I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } 8 }\
#{ S:Generic:Repeated { S:Generic:Above {I:SMA 5 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } \
#{ I:SMA 30 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } 5} \
#{ S:Generic:Repeated { S:Generic:Above {I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } \
#{ I:SMA 30 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } 3} \
#{ S:Generic:Above {I:SMA 5 {I:MFI}} 50 } \
#{ S:Generic:Above {I:SMA 20 {I:ADX} } 30}\
#{ S:Generic:Repeated {S:Generic:Increase {I:SMA 50} } 5 }\


#{ S:Generic:Above {I:Prices CLOSE} {I:SMA 50 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} }}\
# ====== 新模式测试  =============#
#buy_signal = """ { S:Generic:And \
#{ S:Generic:Above {I:MACD/3} 0 }\
#{ S:Generic:Repeated { S:Generic:Above {I:SMA 5 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } \
#{ I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } 10}\
#{ S:Generic:Increase {I:Generic:Eval {I:SMA 5 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}}} - \
#{ I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } } \
#} {S:Generic:False } """

#{ S:Generic:Increase {I:SMA 50 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}}}  } \
#{ S:Generic:Repeated { S:Generic:Above {I:SMA 5 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } \
#{ I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } 5}\
#{ S:Generic:Above {I:ADX}  30}\
#{ S:Generic:Above {I:Generic:Eval {I:SMA 5 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}}} - \
#{ I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } {I:Generic:Eval 0.5*{I:ATR 40}} } \
#{ S:Generic:Above {I:SMA 5 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } { I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } \
#{ S:Generic:Above {I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } { I:SMA 25 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } \
#{ S:Generic:Repeated { S:Generic:Above {I:SMA 5 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } \
#{ I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } 8 }\
#{ S:Generic:Repeated { S:Generic:Above {I:SMA 5 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } \
#{ I:SMA 30 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } 5} \
#{ S:Generic:Repeated { S:Generic:Above {I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } \
#{ I:SMA 30 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } 3} \
#{ S:Generic:Above {I:SMA 5 {I:MFI}} 50 } \
#{ S:Generic:Above {I:SMA 20 {I:ADX} } 30}\
#{ S:Generic:Repeated {S:Generic:Increase {I:SMA 50} } 5 }\

#buy_signal = """ { Signals::Generic::And \
#{ S:Generic:Repeated {S:Generic:Increase {I:SMA 200} } 30 } \
#{ S:Generic:Above {I:ADX} 30} \
#{ S:Generic:Increase {I:ADX} }\
#{ S:Generic:Above {I:MACD/3} 0 }\
#} {S:Generic:False } """
#{ S:Generic:Above {I:Prices CLOSE} {I:SMA 200 {I:Prices CLOSE} } } \
#{ S:Generic:Increase {I:STO/4} }\
#{ S:Generic:CrossOverUp {I:STO/4} 25 }\
#{ S:Generic:CrossOverUp {I:STO/1} 30 }\
#{ S:Generic:Above {I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } {I:SMA 25 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } }\
#{ S:Generic:Above {I:MACD/3} 0 }\
#{ S:Generic:Above {I:ADX} 30 } \
#{ S:Generic:Increase {I:MACD} }\
#{ S:Generic:Above {I:SMA 5 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } {I:SMA 25 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } }\
#{ S:Generic:Above {I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } {I:SMA 25 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } }\


#======== Macd系统测试 随机 ==========#
#buy_signal = """ { S:Generic:And \
#{ S:Generic:Repeated {S:Generic:Increase {I:SMA 200} } 30 }\
#{ S:Generic:Above {I:Prices CLOSE} {I:SMA 200 {I:Prices CLOSE} } } \
#{ S:Generic:Above {I:MACD/3} 0 }\
#{ S:Generic:Above {I:SMA 5 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } {I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } }\
#{ S:Generic:CrossOverUp {I:STO/4} 25 } } {S:Generic:False } """

##======== Macd系统测试 ==========#
#buy_signal = """ { S:Generic:And \
#{ S:Generic:Repeated {S:Generic:Increase {I:SMA 200} } 30 }\
#{ S:Generic:Repeated {S:Generic:Above {I:SMA 50} {I:SMA 200} } 20} \
#{ S:Generic:Above {I:Prices CLOSE} {I:SMA 200 {I:Prices CLOSE} } } \
#{ S:Generic:Above {I:MACD/3} 0 }\
#{ S:Generic:CrossOverUp {I:STO/4} 25 } } {S:Generic:False } """

# ===== 强势测试 ==================#
buy_signal = """ { Signals::Generic::And \
{ S:Generic:Repeated {S:Generic:Above {I:SMA 50} {I:Generic:PeriodAgo 5 {I:SMA 50}}} 5 } \
{ S:Generic:Repeated {S:Generic:Above {I:SMA 20} {I:Generic:PeriodAgo 5 {I:SMA 20}}} 10 } \
{ S:Generic:Above {I:SMA 20} {I:SMA 50} } \
{ S:Generic:Above {I:SMA 50} {I:SMA 200} } \
{ S:Generic:Below {I:STO/1} 20 }} {S:Generic:False } """

#======== 突破系统测试 ==========#
#buy_signal = """ { S:Generic:And \
#{ S:Generic:Repeated {S:Generic:Increase {I:SMA 200} } 30 }\
#{ S:Generic:Repeated {S:Generic:Above {I:SMA 50} {I:SMA 200} } 20} \
#{ S:Generic:Above {I:Prices CLOSE} {I:SMA 200 {I:Prices CLOSE} } } \
#{ S:Generic:Above {I:Prices CLOSE} {I:Generic:Eval 1.02* { I:Generic:PeriodAgo 1 {I:Generic:MaxInPeriod 20 {I:Prices HIGH}} }  }} \
#{ S:Generic:Below {I:Prices CLOSE} {I:Generic:Eval 1.05* { I:Generic:PeriodAgo 1 {I:Generic:MaxInPeriod 20 {I:Prices HIGH}} }  }} \
#{ S:Generic:Above {I:Prices VOLUME} {I:Generic:Eval 1.5*{I:SMA 50 {I:Prices VOLUME}}}} \
#} {S:Generic:False } """

#======== 原始测试基础修改测试 ==========#
#buy_signal = """ { S:Generic:And \
#{ S:Generic:Repeated {S:Generic:Increase {I:SMA 200} } 30 }\
#{ S:Generic:Increase {I:Generic:Eval  {I:SMA 20} - {I:SMA 50}} } \
#{ S:Generic:Repeated {S:Generic:Above {I:SMA 50} {I:SMA 200} } 20} \
#{ S:Generic:Above {I:Prices CLOSE} {I:SMA 200 {I:Prices CLOSE} } } \
#{ S:Generic:CrossOverUp {I:STO/4} 25 } } {S:Generic:False } """

#======== 原始测试的 ==========#
#buy_signal = """ { S:Generic:And \
#{ S:Generic:Repeated {S:Generic:Increase {I:SMA 200} } 30 }\
#{ S:Generic:Increase {I:Generic:Eval  {I:SMA 50} - {I:SMA 200}} } \
#{ S:Generic:Repeated {S:Generic:Above {I:SMA 50} {I:SMA 200} } 20} \
#{ S:Generic:Above {I:Prices CLOSE} {I:SMA 200 {I:Prices CLOSE} } } \
#{ S:Generic:CrossOverUp {I:STO/4} 25 } } {S:Generic:False } """

#close_signal = """ { S:Generic:Below {I:Prices CLOSE} {I:Generic:PeriodAgo 5 { I:Generic:Eval {I:Prices CLOSE} - 1.5*{I:ATR 40} }} } """
#close_signal = """ { S:Generic:Below {I:Prices CLOSE} {I:Generic:PeriodAgo 5 {I:SMA 5{ I:Generic:Eval {I:Prices CLOSE} - 1.5*{I:ATR 40} }}} } """
#close_signal = """ { S:Generic:Below {I:Prices CLOSE} {I:SMA 10{ I:Generic:Eval {I:Prices CLOSE} - 1.5*{I:ATR 40} }} } """
#close_signal = """ { S:Generic:Decrease {I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 1.5*{I:ATR 40}} } } """
#close_signal = """ { S:Generic:CrossOverDown {I:SMA 5 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } {I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } } """
close_signal = """ { S:Generic:And \
{ S:Generic:Below {I:MACD/3} 0 }\
{ S:Generic:Below {I:SMA 5 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } {I:SMA 10 {I:Generic:Eval {I:Prices CLOSE} - 2*{I:ATR 40}} } }\
} """

#close_signal = """ { S:Generic:And \
#{ S:Generic:Above {I:MACD/3} 0 }\
#} """
#close_signal = """ {S:Generic:Decrease {I:SMA 10}} """
#sell_signal ="--close-strategy='Stop::Breakeven'" 
#sell_signal ="--close-strategy='Stop::ExtremePrices 5 2'" 
#sell_signal ="--close-strategy='OppositeSignal'" 
sell_signal_must ="--close-strategy='Stop::Fixed 8'" 
sell_signal_1 ="--close-strategy='Generic %s {S:Generic:False}' " % (close_signal)
sell_signal_2 ="--close-strategy='CloseGain 25'"
#sell_signal = "%s %s %s " % (sell_signal_must,sell_signal_1,sell_signal_2)
sell_signal = "%s %s " % (sell_signal_must,sell_signal_1)
#sell_signal = " %s " % (sell_signal_1)
#command = """cd /home/hua.fu/geniustrader/Scripts;./backtest.pl --full --money-management="Basic" --timeframe day --trade-filter="LongOnly" \
#--trade-filter="MaxOpenTrades 1" --system='Generic %s ' %s %s """ % (buy_signal,sell_signal,symbol)
#command = """cd /home/hua.fu/geniustrader/Scripts;./backtest.pl --money-management="Basic" --timeframe day --trade-filter="LongOnly" \
#--trade-filter="MaxOpenTrades 1" --system='TTS' %s %s """ % (sell_signal,symbol)
test_list = []
back_list = ['IBM','AIG','FNSR','HANS','AEA','FSLR','RIG','AMZN','CIM','NRF','BAC']

if symbol:
    test_list.append(symbol)
else:
    test_list = back_list

report_file = open(report_tpl,"w")

for symbol in test_list:
    command = """cd /home/hua.fu/geniustrader/Scripts;./backtest.pl  --money-management="Basic" --timeframe day --trade-filter="LongOnly" \
    --trade-filter="MaxOpenTrades 1" --system='Generic %s ' %s %s """ % (buy_signal,sell_signal,symbol)
    (status,output) = commands.getstatusoutput(command)
    print "symbol = %s complete" % symbol
    if len(test_list) == 1:
        print output
    report_file.writelines(output + "\n")

report_file.close()
