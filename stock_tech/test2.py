# coding=utf-8       
from lxml import *  
import lxml.html  
import urllib2  
import lxml.html as H  
  
def getjarinfo(url):  
    c=urllib2.urlopen(url)  
      
    f=c.read()  
    doc = H.document_fromstring(f)  
    tables=doc.xpath("//table[@id='xiazai']")      
    pinpais=doc.xpath("//td[@id='pinpai']")  
    jixings=doc.xpath("//div[@id='jixing']")  
    jars = doc.xpath("//table[@id='xiazai']//tr[2]/td[1]/a[1]")  
    for j in range(len(pinpais)):  
      print jars[j].get('href')  
      print pinpais[j].text_content()           
      print jixings[j].text_content()  
    e=doc.xpath(u"//div[text()='%s']" % u"游戏介绍")  
    describe=e[0].getnext().text_content()  
    #r = doc.xpath("//table[@id='xiazai']//tr[2]/td[1]/a[1]")[0]  
    #jarurl=r.get('href')  
      
if __name__ == '__main__':  
    url='http://game.3533.com/game/30862.htm'  
    getjarinfo(url)  
