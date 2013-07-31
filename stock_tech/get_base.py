#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
get stock base info
"""
__version__ = 0.1

import urllib,sys,os,time
from BeautifulSoup import BeautifulSoup
from operator import itemgetter
#content = urllib.urlopen(url).read()

#fd = open('osg')
#content = fd.read()
#fd.close()

def get_cache_file(cache_file,symbol):
    """
    网站获取数据
    """
    if not os.path.isfile(cache_file) or (int(time.time()) - int(os.stat(cache_file).st_mtime) >= 86400):
        url = "http://finviz.com/quote.ashx?t=%s" % symbol
        content = urllib.urlopen(url).read()
        fd = open(cache_file,"w")
        fd.writelines(content)
        fd.close()
        return content
    else:
        content=open(cache_file).read()
        return content

def get_info_dict(content):
    """
    分析数据，得到字典格式数据
    """
    soup = BeautifulSoup(content)
    b = soup.findAll('tr',{"class":"table-dark-row"})
    base_dict = {}
    for item in b:
        count = 1
        last_key = None
        for td in item.findAll('td'):
            if td:
                if count % 2 == 0:
                    base_dict[last_key] = td.text
                else:
                    #if td.text.find("Earnings") != -1: continue
                    last_key = td.text
            count = count +1
    #print base_dict
    sort_aa = sorted(base_dict.items(),key=itemgetter(0))
    #for k,v in base_dict.items():
    for item in sort_aa:
        k,v = item
        if k.find("Earnings") != -1: continue
        #print "%s = %s " % (k,v)
        #continue
        if k.find("EPS") != -1 or k.find("Debt") != -1 or k.find("Target Price") != -1\
                or k.find("Book") != -1 or k.find("Cash") != -1 \
                or k.find("Sales") != -1 or k.find("RO") != -1 or k.find("Dividend") != -1 or k.find("P/") != -1:
            print "%s = %s " % (k,v)

def main():
    """
    main program
    """
    try:
        symbol = sys.argv[1]
        symbol = symbol.upper()
    except Exception,e:
        print "Lack of symbol,exit"
        sys.exit(1)
    
    base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    cache_tmp ="%s/tmp" % (base_dir) 
    cache_file = "%s/%s" % (cache_tmp,symbol)
    content = get_cache_file(cache_file,symbol)
    get_info_dict(content)

if __name__ == "__main__":
        main()

