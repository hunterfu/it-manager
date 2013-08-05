#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
from time import strftime,gmtime
import datetime
import commands
import re
# 定义变量 
base_dir,cur_dir = os.path.split(os.path.abspath(sys.argv[0]))
html_template = "%s/index.html" % base_dir

def server_local_time():
    localtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return localtime

def server_gmt_time():
    gmttime = strftime("%Y-%m-%d %H:%M:%S +0000", gmtime())
    return gmttime

def os_release():
    release="未知"
    if os.path.isfile("/etc/redhat-release"):
        out = os.popen("cat /etc/redhat-release")
        release = out.read()
    if os.path.isfile("/etc/fedora-release"):
        out=os.popen("cat /etc/fedora-release")
        release = out.read()
    return release

def print_header():
    print ''' 
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml"> 
<head> 
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" /> 
<title>CGI环境探针 V1.0 (PYTHON版本)</title> 
<meta name="keywords" content="python探针,探针程序,python探针程序,探针,cgi" /> 
<meta name="author" content="北方人 - hunterfu2009 (a) gmail com - 运维之道">
<style type="text/css"> 
<!--

table { solid #41433E;  margin-bottom:10px; }
td,th { padding:4px;background-color:#F0F0F0;  }
th { background:#8FAEBE; color:#343525; text-align:left;}
h1 {
    background : #8faebe;
    font-size: large;
    color : white;
    padding : 10px;
    margin-top : 0px;
    margin-bottom : 20px;
    text-align : center;
}
-->
</style> 
</head> 
<body> 
<h1> CGI服务器探针 V1.0 (PYTHON版)</h1>

<!-- 页头 --> 
<p align=center>
 <a href="#one">服务器信息</a> 
 <a href="#two">Python基本信息</a> 
 <a href="#three">模块信息</a> 
 <a href="#four">系统命令信息</a> 
</p>
    '''

# search path 
l_time = server_local_time()
g_time = server_gmt_time()
release = os_release()

# check module list
mod_list = ['cgitb','smtplib','pysqlite2']

# check cmd available list
cmd_list = ['dig','gzip','tar','sendmail','sed','awk','grep','sh','curl']

# test cmd
check_cmd = {}
check_cmd['dig'] = "dig @ns1.google.com www.google.com +short"
check_cmd['curl'] = "curl -s -I http://www.sina.com"

def print_server_info():
    print '''
<!-- 服务器基础信息 --> 
<table border="0" cellspacing="2" cellpadding="0" align=center width=80%> 
    <tr><th colspan=2> 服务器基础信息 <a name="one" id="one"></a> </th> </tr> 
    '''
    print "<tr><td>服务器时间(本地)</td><td>%s</td></tr>" % (l_time)
    print "<tr><td>服务器时间(GMT)</td><td>%s</td></tr>" % (g_time) 
    print "<tr><td>服务器域名/IP地址</td><td>%s(%s)</td></tr>" % (os.environ['SERVER_NAME'],os.environ['SERVER_ADDR']) 
    print "<tr><td>服务器操作系统</td><td>系统类型:%s<br/>发行版本:%s</td></tr>" % (sys.platform,release) 
    print "<tr><td>WEB服务器版本</td><td>%s</td></tr>" %(os.environ['SERVER_SOFTWARE']) 
    print "<tr><td>WEB服务器签名</td><td>%s</td></tr></table>" % (os.environ['SERVER_SIGNATURE'])

def print_base_info():
    print '''
<!-- 基本信息  --> 
<table width="80%" cellpadding="0" cellspacing="2" border="0" align=center > 
    <tr><th colspan="2"> 基本信息 <a name="two" id="two"></a></th></tr> 
    '''
    print "<tr><td>Python版本</td><td>%s</td></tr>" % (sys.version) 
    print "<tr><td>Python模块搜索路径<td>%s</td></tr></table>" % ("<br>".join(sys.path))
   
def print_module_info():
    print '''
<!-- 模块信息 --> 
<table width="80%" cellpadding="0" cellspacing="2" border="0" align=center> 
    <tr> <th colspan="3">常用模块信息 <a name="three" id="three"></a> </th> </tr> 
    '''
    mod_msg = ""
    mod_version = "&nbsp;"
    for mod in mod_list: 
        try:
            __import__(mod)
            mod_msg = "已安装"
        except Exception,e:
            mod_msg =  "未安装"
            pass
        print "<tr><td >%s</td><td >%s</td><td ><code>%s</code></td></tr>" % (mod,mod_msg,mod_version)
    print "</table>"

def print_cmd_info():
    print '''
    <!-- 命令信息 --> 
    <table width="80%" cellpadding="0" cellspacing="2" border="0" align=center> 
        <tr> <th colspan="3"> 命令信息 <a name="four" id="four"></a> </th> </tr> 
    '''
    
    for cmd in cmd_list: 
        (status,output) =  commands.getstatusoutput("which %s" % cmd)
        cmd_test_output = "&nbsp;"
        if status == 0:
            if check_cmd.has_key(cmd):
                cmd_test = check_cmd[cmd]
                out = os.popen(cmd_test) 
                cmd_test_output = out.read()
                result = re.sub(r'\r\n', '<br>', cmd_test_output)
                result.strip()
                cmd_test_output = "<b><font color=red>Test Cmd : "+cmd_test+"</font></b><br>"+result
        else:
            output = "未安装"
        print "<tr><td width=10%%>%s</td><td width=25%%>%s</td><td width=65%%>%s</td></tr>" % (cmd,output,cmd_test_output) 
    
    print "</table>"

def print_footer():
    print '''
<hr size='1' width=85%>
<p align="center"><a href="http://www.51know.info">&nbsp;运维之道出品&nbsp;</a>版权所有&copy; 2010-2012</p>
</body> 
</html> 
    '''

def main():
    print_header()
    print_server_info()
    print_base_info()
    print_module_info()
    print_cmd_info()
    print_footer()

print "Content-type:text/html\r\n\r\n"
main()
