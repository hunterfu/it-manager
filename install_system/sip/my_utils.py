# -*- coding:utf-8 -*-
import socket, struct
import StringIO, csv


def ip_to_n(ip):
    return socket.ntohl(struct.unpack("I",socket.inet_aton(ip))[0])


def upfile_to_reader(file):
    cont = file.read()
    cont = cont.decode('gb2312')
    s = StringIO.StringIO()
    s.write(cont.encode('utf-8'))
    s.seek(0)
    reader = csv.reader(s)
    return reader

class UnicodeWriter:
    def __init__(self,f,encoding='utf8'):
        self.writer = csv.writer(f)
	self.encoding = encoding

    def writerow(self, row):
        self.writer.writerow([s.encode(self.encoding) for s in row])
