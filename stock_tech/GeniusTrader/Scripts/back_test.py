#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = 0.1

import urllib,urllib2,sys
from pprint import pprint
from BeautifulSoup import BeautifulSoup
from sys import argv
import commands


try:
    symbol = argv[1]
except Exception,e:
    print "Please Input Ip which you want remove"
    sys.exit(1)

symbol = symbol.upper()

# back test command

#buy_signal = """ { S:Generic:And \
#{ S:Generic:Repeated {S:Generic:Increase {I:SMA 200} } 20 }\
#{ S:Generic:Increase { I:Generic:Eval  {I:SMA 50} - {I:SMA 200} }} \
#{ S:Generic:Repeated {S:Generic:Above {I:SMA 50} {I:SMA 200} } 20} \
#{ S:Generic:Above {I:Prices CLOSE} {I:SMA 200 {I:Prices CLOSE} } } \
#{ S:Generic:CrossOverUp {I:STO/4} 20 } } {S:Generic:False } """

buy_signal = """ { S:Generic:And \
{ S:Generic:Repeated {S:Generic:Increase {I:SMA 200} } 20 }\
{ S:Generic:Repeated {S:Generic:Above {I:SMA 50} {I:SMA 200} } 20} \
{ S:Generic:Above {I:Prices CLOSE} {I:SMA 200 {I:Prices CLOSE} } } \
{ S:Generic:CrossOverUp {I:STO/4} 20 } } {S:Generic:False } """
close_signal = """ { S:Generic:Repeated { S:Generic:Below {I:SMA 10}  {I:Generic:PeriodAgo 1 {I:SMA 10}} } 10} """
#close_signal = """ {S:Generic:Decrease {I:SMA 10}} """
#sell_signal ="--close-strategy='Stop::Breakeven'" 
#sell_signal ="--close-strategy='Stop::ExtremePrices 5 2'" 
#sell_signal ="--close-strategy='OppositeSignal'" 
sell_signal_must ="--close-strategy='Stop::Fixed 5'" 
#sell_signal ="--close_strategy='Indicators::Generic::Eval  {I:Prices CLOSE} - 1.5*{I:ATR}'"
#sell_signal_1 ="--close-strategy='Generic %s {S:Generic:False}' " % (close_signal)
sell_signal_1 ="--close-strategy='CloseGain'"
sell_signal = "%s  %s" % (sell_signal_must,sell_signal_1)
command = """cd /home/hua.fu/geniustrader/Scripts;./backtest.pl --money-management="Basic" --timeframe day --trade-filter="LongOnly" \
--trade-filter="MaxOpenTrades 1" --system='Generic %s ' %s %s """ % (buy_signal,sell_signal,symbol)

(status,output) = commands.getstatusoutput(command)
print output

