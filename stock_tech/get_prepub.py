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

def get_cache_file(cache_file):
    """
    网站获取数据
    """
    if not os.path.isfile(cache_file) or (int(time.time()) - int(os.stat(cache_file).st_mtime) >= 86400):
        url = "http://pesystem.taobao.org:9999/app/alimall"
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
    b = soup.findAll('div',{"class":"app-list app-table-container"})
    base_dict = {}
    key_list = []
    val_list = []
    item = b[5]
    count = 1
    for tr in item.findAll('tr'):
        #print tr
        #print "=======" * 20 
        if count % 2 == 1:
            for th in tr.findAll('th'):
                key_list.append(th.text)
        if count % 2 == 0:
            for td in tr.findAll('td'):
                i =0 
                print "%s = %s" % (key_list[i],td.text)
                i = i +1
            key_list = []
        count = count +1


def main():
    """
    main program
    """
    #try:
    #    symbol = sys.argv[1]
    #    symbol = symbol.upper()
    #except Exception,e:
    #    print "Lack of symbol,exit"
    #    sys.exit(1)
    
    base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    cache_tmp ="%s/tmp" % (base_dir) 
    cache_file = "%s/alimall" % (cache_tmp)
    content = get_cache_file(cache_file)
    get_info_dict(content)

if __name__ == "__main__":
        main()

