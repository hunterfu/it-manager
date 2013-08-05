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
my $site_conf="./site.conf";

# 是否还有url还没有访问过,只是在间隔时间内没有找到符合间隔时间的url
my $time_out="false";

tie my %h, "BerkeleyDB::Hash",
-Filename => $url_dbfile,
-Flags    => DB_CREATE
        or die "Cannot open file $url_dbfile: $! $BerkeleyDB::Error\n";


while (my ($k, $v) = each %h)
{
    print "key = $k || val = $v\n" ;  
}


