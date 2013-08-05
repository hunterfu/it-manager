#!/usr/bin/env perl
print "Content-type:text/html\n\n";

sub server_local_time{
    my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
    my @months = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec");
    my $date = sprintf("%02d-%s-%04d",$mday,$months[$mon],$year+1900);
    my $time = sprintf("%02d:%02d:%02d",$hour,$min,$sec);
    my $localtime = "$date, $time";
    return $localtime;
}

sub server_gmt_time{
    my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = gmtime(time);
    my @months = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec");
    my $date = sprintf("%02d-%s-%04d",$mday,$months[$mon],$year+1900);
    my $time = sprintf("%02d:%02d:%02d",$hour,$min,$sec);
    my $gmttime = "$date, $time";
    return $gmttime;
}

sub os_release{
    my $release="未知";
    if (-e "/etc/redhat-release" )
    {
       $release=`cat /etc/redhat-release`;
    }
    if (-e "/etc/fedora-release")
    {
       $release=`cat /etc/fedora-release`;
    }
    return $release
}

# search path 
my $inc_path = join("<br />",@INC);
my $l_time = &server_local_time;
my $g_time = &server_gmt_time;
my $release = &os_release;

# check module list
my @mod_list = ('CGI','HTML::Template','CGI::Cookie','DBI','DBD::mysql','Image::Size','GD','Image::Magick','Net::SMTP','MIME::Lite');

# check cmd available list
my @cmd_list = ('dig','gzip','tar','sendmail','sed','awk','grep','sh','curl');

# test cmd 

my %check_cmd = ();
$check_cmd{'dig'} = "dig \@ns1.google.com www.google.com +short";
$check_cmd{'curl'} = "curl -s -I http://www.sina.com";

print <<HEADER; 
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml"> 
<head> 
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" /> 
<title>CGI环境探针 V1.0 (PERL版本)</title> 
<meta name="keywords" content="perl探针,探针程序,perl探针程序,探针" /> 
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
HEADER

print <<TITLE;
<h1> CGI服务器探针 V1.0 (PERL版)</h1>

<!-- 页头 --> 
<p align=center>
 <a href="#one">服务器信息</a> 
 <a href="#two">perl基本信息</a> 
 <a href="#three">模块信息</a> 
 <a href="#four">系统命令信息</a> 
</p>
TITLE
print <<SERVER_INFO;
<!-- 服务器基础信息 --> 
<table border="0" cellspacing="2" cellpadding="0" align=center width=80%> 
    <tr><th colspan=2> 服务器基础信息 <a name="one" id="one"></a> </th> </tr> 
    <tr><td>服务器时间(本地)</td><td>$l_time</td></tr> 
    <tr><td>服务器时间(GMT)</td><td>$g_time</td></tr> 
    <tr><td>服务器域名/IP地址</td><td>$ENV{'SERVER_NAME'}($ENV{'SERVER_ADDR'})</td></tr> 
    <tr><td>服务器操作系统</td><td>系统类型:$^O<br/>发行版本:$release</td></tr> 
    <tr><td>WEB服务器版本</td><td>$ENV{'SERVER_SOFTWARE'}</td></tr> 
    <tr><td>WEB服务器签名</td><td>$ENV{'SERVER_SIGNATURE'}</td></tr> 
</table> 
SERVER_INFO

print <<BASE_INFO;
<!-- 基本信息  --> 
<table width="80%" cellpadding="0" cellspacing="2" border="0" align=center > 
    <tr><th colspan="2"> 基本信息 <a name="two" id="two"></a></th></tr> 
    <tr><td>PERL版本</td><td>$]</td></tr> 
    <tr><td>PERL模块搜索路径<td>$inc_path</td></tr> 
</table> 

BASE_INFO

print <<MODULE_INFO;
<!-- 模块信息 --> 
<table width="80%" cellpadding="0" cellspacing="2" border="0" align=center> 
    <tr> <th colspan="3">常用模块信息 <a name="three" id="three"></a> </th> </tr> 
MODULE_INFO

for my $mod (@mod_list) 
{
    eval("use $mod;");
    my $mod_msg = "未安装";
    my $mod_version = "&nbsp;";
    if (!$@) { 
        $mod_msg = "已安装";
        $mod_version = $mod->VERSION;
    }
    print qq{
        <tr> 
            <td >$mod</td> 
            <td >$mod_msg</td> 
            <td ><code>$mod_version</code></td> 
        </tr>}; 
}

print qq{</table>};

print <<CMD_INFO;
<!-- 命令信息 --> 
<table width="80%" cellpadding="0" cellspacing="2" border="0" align=center> 
    <tr> <th colspan="3"> 命令信息 <a name="four" id="four"></a> </th> </tr> 
CMD_INFO

for my $cmd (@cmd_list) 
{
    my $output=`which $cmd`;
    my $cmd_test_output = "&nbsp;";
    if ($output=~"/")
    {
        if ($check_cmd{$cmd})
        { 
            $cmd_test_output = `$check_cmd{$cmd}`; 
            chomp($cmd_test_output);
            $cmd_test_output =~ s/\r\n/<br>/g;
            $cmd_test_output = "<b><font color=red>Test Cmd : ".$check_cmd{$cmd}."</font></b><br>".$cmd_test_output;
        }
    }
    else
    {
        $output="未安装"
    }
    print qq{
        <tr> 
            <td >$cmd</td> 
            <td >$output</td> 
            <td>$cmd_test_output</td>
        </tr>}; 
}
print qq{</table>};

print <<FOOTER;
<hr size='1' width=85%>
<p align="center"><a href="http://www.51know.info">&nbsp;运维之道出品&nbsp;</a>版权所有&copy; 2010-2012</p>
</body> 
</html> 

FOOTER

