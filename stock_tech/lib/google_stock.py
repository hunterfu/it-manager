#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#
#  Copyright (c) 2010-2011, Chang Lan(changlan9@gmail.com)
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.


import urllib
import xml.etree.ElementTree as etree
import sys,os

"""
This is the "googlestockquote" module.

This module provides a Python API for retrieving stock data from Google Stock API.

sample usage:
>>> import googlestockquote
>>> print googlestockquote.get_price('GOOG')
529.46
"""


def __request(symbol,stat):
    url = 'http://www.google.com/ig/api?stock=%s' % symbol
    xmldoc = etree.fromstring(urllib.urlopen(url).read())
    return xmldoc.find('finance/%s' % stat).get('data')
    
       
    
def get_price(symbol): 
    return __request(symbol, 'last')


def get_change(symbol):
    return __request(symbol, 'change')
    
    
def get_volume(symbol): 
    return __request(symbol, 'volume')


def get_avg_daily_volume(symbol): 
    return __request(symbol, 'avg_volume')
    
    
def get_stock_exchange(symbol): 
    return __request(symbol, 'exchange')
    
    
def get_market_cap(symbol):
    return __request(symbol, 'market_cap')
   
   
def get_percentage_change(symbol):
    return __request(symbol, 'perc_change')

def get_currency(symbol):
    return __request(symbol, 'currency')

def get_daily_high(symbol):
    return __request(symbol, 'high')

def get_daily_low(symbol):
    return __request(symbol, 'low')

def get_open(symbol):
    return __request(symbol, 'open')

def get_yearly_close(symbol):
    return __request(symbol, 'y_close')

def get_company(symbol):
    return __request(symbol, 'company')

if __name__ == "__main__":
    try:
        print get_company(sys.argv[1])
    except:
        pass
