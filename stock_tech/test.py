#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = 0.1

import urllib

url = "http://quotes.money.163.com/0600000.html"

content = urllib.urlopen(url).read()

from BeautifulSoup import BeautifulSoup
soup = BeautifulSoup(content)
#print soup.prettify()
b = soup.findAll('table',{"class":"tbl3","width":"201"},limit=1)
a = b.pop()
print a
上海交易所
http://quotes.money.163.com/hs/download/0601398,20100101,20100630,TDATE;SYMBOL;TCLOSE;HIGH;LOW;TOPEN;VOTURNOVER.csv
深圳交易所
http://quotes.money.163.com/hs/download/1000566,20100101,20100630,TDATE;SYMBOL;TCLOSE;HIGH;LOW;TOPEN;VOTURNOVER.csv

