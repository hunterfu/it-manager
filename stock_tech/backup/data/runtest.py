#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pysqlite2.dbapi2 as sqlite
    
def runTest():
    c = sqlite.connect('test.db')
    cu = cx.cursor()
    
    #create
    cu.execute('''create table catalog(
        id integer primary key,
        pid integer,
        name varchar(10) unique
        )''')

    #insert
    cu.execute('insert into catalog values(0,0,"zrp")')
    cu.execute('insert into catalog values(1,0,"hello")')
    cx.commit()
    
    #select
    cu.execute('select * from catalog')
    print '1:',
    print cu.rowcount
    rs = cu.fetchmany(1)
    print '2:',
    print rs
    rs = cu.fetchall()
    print '3:',
    print rs
    
    #delete
    cu.execute('delete from catalog where id = 1 ')
    cx.commit()
    
    
    cu.execute('select * from catalog')
    rs = cu.fetchall()
    print '4:',
    print rs
    
    #select count
    cu.execute("select count(*) from catalog")
    rs = cu.fetchone()
    print '5:',
    print rs
    
    
    cu.execute("select * from catalog")
    cu.execute('drop table catalog')

if __name__ == '__main__':
    runTest()
