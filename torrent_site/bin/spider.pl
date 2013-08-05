#! /usr/bin/perl

use BerkeleyDB;
#Debug using Data::Dumper
use Data::Dumper;

$| = 1;
# 0=no debug, 1=display progress, 2=complete dump
my $DEBUG = 1;  		


use Cwd 'abs_path';
my $abs_path = abs_path($0);
my $base_dir=`dirname $abs_path`;
chomp($base_dir);
chdir($base_dir);
my $url_dbfile="../data/bdb/spider_url.bdb";
my $torrent_dir="../data/spider_torrent";
my $tmp_file="/tmp/tmp_spider.html";
my $dumptorrent_cmd="./dumptorrent";
my $site_conf="$base_dir/site.conf";

# 是否还有url还没有访问过,只是在间隔时间内没有找到符合间隔时间的url
my $time_out="false";
my $db = new BerkeleyDB::Hash
-Filename => $url_dbfile,
-Flags    => DB_CREATE
        or die "Cannot open file $url_dbfile: $! $BerkeleyDB::Error\n";

# 保留各个站点访问间隔时间的hash
my %access_delay=();

##########################################
# 读取抓取site 列表
##########################################
my @site_list=();
if ( -e "$site_conf" )
{
        open(CONF,$site_conf) or die ("ERROR:Config file is not exist\n");
}
else
{
        print "ERROR:$site_conf Config file is not exist\n";
        exit 1;
}

my @config_list= <CONF>;
close CONF;

foreach my $config_line(@config_list)
{
	my $string = "";
    if ( $config_line =~ /^#/ ) { next;}
    if ( $config_line =~ /^$/ ) { next;}
    #if ( $config_line =~ /^@(\S+)\s+\=\s+(\S+);/ )
	#{  $string = "\@$1=$2";}
    #elsif ( $config_line =~ /^(\S+)\s+\=\s+(\S+);/ )
	#{  $string = "\$$1=$2"; }
    #eval($string);
	eval($config_line);		
}
# 合并网站列表到一个数组中,并加入到url数据库中
my ($contentsw_list,$site_name);
foreach $contentsw_list(@category)
{
    my $string="\@$contentsw_list"."_list";
    my @servers=eval($string);
    foreach $site_name(@servers)
	{
		push(@site_list,"$site_name");
		my $val=DbGet("$site_name");
		if($val eq "") { Updb("$site_name",0); }
	}
}
#print Dumper(\@site_list);
#exit 0;
###########################################
#  get value from bdb
#  #######################################
sub DbGet($)
{
    my $key=shift;
    my $val="";
    if ($db->db_get($key, $val) == 0)
    {
		chomp($val);
    }
	return $val;
}

######################################
# update bdb
#####################################
sub Updb($$)
{
	my $key=shift;
	my $val=shift;
    $db->db_del("$key");
    $db->db_put("$key","$val");
}

######################################
# delete key from bdb
#####################################
sub deldb($)
{
	my $key=shift;
    $db->db_del("$key");
}

$SIG{TERM} = $SIG{INT}=\&exit_prog;

sub exit_prog
{
	my $status = $db->db_sync();
	undef $db;
	print "exit from ctrl + c\n" ;
	exit;
} 
#
#
# Initialize.
my $agent="Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 2.0.50727; MAXTHON 2.0)";

# Load the queue with the first URL to hit.
$thisURL = &find_new();

while($thisURL ne "")
{

	
	# Split the protocol from the URL.
	my ($protocol, $rest) = $thisURL =~ m|^([^:/]*):(.*)$|;

	# Split out the hostname, port and document.
	my ($server_host, $port, $document) = $rest =~ m|^//([^:/]*):*([0-9]*)/*([^:]*)$|;

	# 过滤url,以下url不需要访问，也不用记录到urldb中
	my $reg_filter = "$filter{$server_host}" ;
	if ( $document =~ m|$reg_filter| ) 
	{ 
		print "DEBUG : DELETE URL = $thisURL \n";
		deldb("$thisURL");
		# 继续找下一个没有访问过的url
		$thisURL = &find_new();
		while ($thisURL eq "" && $time_out eq "true" ) 	{	$thisURL = &find_new();	}
		next ;
	}

	# print current access url
	print "DEBUG : CURRENT URL = $thisURL \n";	

	# 下载网页
	my $cmd="wget -t 2 --timeout=5 --user-agent=\"$agent\" -o /tmp/wget.log -O $tmp_file \"$thisURL\"";
	system($cmd);
	my $result=`file $tmp_file  | awk -F : '{print \$2}'`;
	chomp($result);
	if ($result =~ /HTML document text/)
	{
		my $page_text = `cat $tmp_file`;
		chomp($page_text);
		$page_text =~ s|<!--[^>]*-->||g;
	
		my @anchors = $page_text =~ m|<A\s+HREF=['"](.*?)['"]|gi;
		foreach my $anchor (@anchors)
		{
			# exclude javascript from url 
			if ( $anchor =~ m/javascript/i ) {next;}
			# exclude # from url
			if ( $anchor =~ m/^#$/ ) { next;}
			# exclude /  from url
			if ( $anchor =~ m/^\/$/ ) { next;}

			# 过滤url,以下url不需要访问，也不用记录到urldb中
			my $reg_filter = "$filter{$server_host}" ;
			if ( $anchor =~ m|$reg_filter| ) { next ;}

			my $newURL=&fqURL($thisURL,$anchor);
			my $val=DbGet("$newURL");
			#print "DEBGU: val=$val NewURL = $newURL \n";
			#if($val > 0)
			#{
				# 如果url已经访问过，则累计被链接的次数
			#	$val++;
			#	Updb("$newURL",$val);
			#}
			#else
			if ($val eq "")
			{
				# 发现新url记录到数据库中
				($new_host) = $newURL =~ m|^[^:/]*:/*([^/:]*):*[0-9]*/*[^:]*$|;
				if( $new_host eq $server_host)
				#if( grep("$new_host",@site_list) )
				{
					Updb("$newURL",0);
				}
			}
		}
		# 将数据写入bdb
		Updb("$thisURL",1);
	}
	# 如果是种子文件，则检查infohash 如果正确则更新url数据库，以后不用在更新
	elsif ($result =~ /BitTorrent file/)
	{
		my $download_dir="$torrent_dir/$server_host";
		system("mkdir -p $download_dir");
		my $info_hash=`$dumptorrent_cmd -v $tmp_file |grep 'Info Hash' | awk -F : '{print \$2}' | sed -r 's/^\\s+//'`;
		chomp($info_hash);
		if($info_hash ne "" && length($info_hash) == 40 )
		{
			print "DEBUG : FIND NEW TORRENT $info_hash IN $download_dir\n";
			my $cmd="mv $tmp_file $download_dir/$info_hash".".torrent";
			system("$cmd");
			# 如果是torrent种子文件的化,以后在不用更新
			Updb("$thisURL",2);
		}		
	}
	# 最后将url更新成为访问过,非html文件
	else { Updb("$thisURL",3);	}

	# 继续找下一个没有访问过的url
	$thisURL = &find_new();
	while ($thisURL eq "" && $time_out eq "true" )
	{
		sleep(5);
		$thisURL = &find_new();
	}

}

# 同步BDB数据
my $status = $db->db_sync();
undef $db;
exit;

#--------------------------------------------------------------
# Build a fully specified URL.
#--------------------------------------------------------------
sub fqURL
{
	local($thisURL, $anchor) = @_;
	local($has_proto, $has_lead_slash, $currprot, $currhost, $newURL);

	# Strip anything following a number sign '#', because its
	# just a reference to a position within a page.
	$anchor =~ s|(^.*)#[^#]*$|$1|;

	# Examine anchor to see what parts of the URL are specified.
	$has_proto = 0;
	$has_lead_slash=0;
	$has_proto = 1 if($anchor =~ m|^[^/:]+:|);
	$has_lead_slash = 1 if ($anchor =~ m|^/|);
	$has_lead_slash = 2 if ($anchor =~ m/^\w+.*/);

	if($has_proto == 1)
	{

		# If protocol specified, assume anchor is fully qualified.
		$newURL = $anchor;

	}
	elsif($has_lead_slash == 1)
	{

		# If document has a leading slash, it just needs protocol and host.
		($currprot, $currhost) = $thisURL =~ m|^([^:/]*):/+([^:/]*)|;
		$newURL = $currprot . "://" . $currhost . $anchor;

	}	
	elsif($has_lead_slash == 2)
	{
           	($currprot, $currhost) = $thisURL =~ m|^([^:/]*):/+([^:/]*)|;
                $newURL = $currprot . "://" . $currhost ."/". $anchor;	
	}
	else
	{

		# Anchor must be just relative pathname, so append it to current URL.
		($newURL) = $thisURL =~ m|^(.*)/[^/]*$|;
		$newURL .= "/" if (! ($newURL =~ m|/$|));
		$newURL .= $anchor;

	}
	if($DEBUG >=2)
	{
		print "Link Found\n   In:$thisURL\n   Anchor:$anchor\n   Result: $newURL\n"
	}
	return $newURL;
}

#---------------------------------------------------------------
# 取最新没有访问过的URL
#---------------------------------------------------------------

sub find_new()
{
	# 默认设置 不存在未访问过的url
	$time_out="false";
	my ($k, $v) = ("", "") ;
	my $cursor = $db->db_cursor();
	#while ($cursor->c_get($k, $v, DB_NEXT) == 0)
	my $current_time = time();
	while ($cursor->c_get($k, $v, DB_PREV) == 0)
	{ 
		if($v == 0)
		{
			# 还存在没有访问过的url
			$time_out="true";
			# Split the protocol from the URL.
			($protocol, $rest) = $k =~ m|^([^:/]*):(.*)$|;
			# Split out the hostname, port and document.
			($server_host, $port, $document) = $rest =~ m|^//([^:/]*):*([0-9]*)/*([^:]*)$|;
			if ( "$server_host" eq "") { print "DEBUG : Current Url = $k || rest = $rest\n"; next; }

			# 每一个站点访问限制，每个站点连续访问间隔10秒
			my $val=$access_delay{"$server_host"};
			if($val ne "")
			{
				if($current_time - $val >= 15)
				{
				        $access_delay{"$server_host"}=$current_time;
						return "$k";
				}
			}
			else
			{
				$access_delay{"$server_host"}=$current_time;
				return "$k";
			}
		}
	}
	undef $cursor;
	return "";
}


