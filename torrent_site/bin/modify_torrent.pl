#!/usr/bin/perl
#************************************************************************************************************#
# ScriptName:           modify_torrent.pl 
# Author:               hua.fu <hua.fu@alibaba-inc.com>            
# Date:                 2010-03-29                 
# Modify Author:        Hua.fu <hua.fu@alibaba-inc.com> 
# Modify Date:          2010-03-29            
# Function:             分析和修改torrent种子文件         
#************************************************************************************************************# 
use BerkeleyDB;
#use strict;
#Debug using Data::Dumper
use Data::Dumper;
#
use Cwd 'abs_path';
my $abs_path = abs_path($0);
my $base_dir=`dirname $abs_path`;
chomp($base_dir);
chdir($base_dir);
my $torrent_dbfile="../data/bdb/torrent.bdb";
my $torrent_dir="../data/spider_torrent";
my $tmp_file="/tmp/tmp_bitfile";
my $dumptorrent_cmd="./dumptorrent";
# 存放下载的torrent文件
my $download_torrent_dir="../web_root/torrent";

my @announce_list_add = ('http://tracker.openbittorrent.com:80/announce','udp://tracker.openbittorrent.com:80/announce','http://tracker.publicbt.com:80/announce','udp://tracker.publicbt.com:80/announce'); 

my $my_annouce= "http://www.51know.info/tracker/announce.php";

my $db = new BerkeleyDB::Hash
-Filename => $torrent_dbfile,
-Flags    => DB_CREATE
        or die "Cannot open file $torrent_dbfile: $! $BerkeleyDB::Error\n";

###########################################
#  get value from bdb
########################################
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

#####################################
# modify torrent file
#####################################
sub modify {
	my $read_file = shift;
	my $read = bdecodefile($read_file);
	my @announce = ();
	my %used;
	my $deladd_match = 0;
    if (!$read) {  $read = bdecode($read_file); }

	my $old_announce = $read->{'announce'};
	$read->{'announce'} = "$my_annouce";
	
	# 添加 到 announce-list
	unshift(@announce_list_add,"$old_announce");
	my $uhx = -1;
	my $ahx = -1;
	foreach my $uh (@{$read->{'announce-list'}}) 
	{
		$uhx++;
		my $uhhx = -1;
		my $add_ahx = 0;
		foreach my $uhh (@{$uh}) 
		{
			$uhhx++;
			if (!$add_ahx) 
			{
				$add_ahx = 1;
				$ahx++;
			}
			$announce[$ahx] = [] if (!$announce[$ahx]);
			push(@{$announce[$ahx]},$read->{'announce-list'}[$uhx][$uhhx]);
		}
	}
	foreach my $announce_add (@announce_list_add)
	{
		$ahx++;
		push(@{$announce[$ahx]},$announce_add);
	}
	$read->{'announce-list'} = [@announce];
	return bencode($read);
}
#####################################
# bencode file 
#####################################
sub bencode {
    my $data = shift;
    my $enc = '';
    if (ref($data) eq 'HASH') {
	no locale;
	foreach (sort(keys %{$data})) {
	    $enc .= bencode($_) . bencode($data->{$_});
	}
	return('d' . $enc . 'e');
    }
    if (ref($data) eq 'ARRAY') {
	foreach (@{$data}) { $enc .= bencode($_); }
	return('l' . $enc . 'e');
    }
    if ($data =~ /^\d+$/) {
	return('i' . $data . 'e');
    }
    return(join(':', length($data), $data));
}

#####################################
# bencode file 
#####################################
sub bdecodefile {
    my $data = shift;
    my $pref = shift;
    my $c = substr($data, $$pref, 1);
    if ($c eq 'd') {
	# hash
	$$pref++;		# eat the 'd'
	my %d = ();
	while (substr($data, $$pref, 1) ne 'e') {
	    my $key = bdecodefile($data, $pref);
	    $d{$key} = bdecodefile($data, $pref);
	    if ($_btdead)  {
		undef($_btdead);
		return 0;
	    }
	}
	$$pref++;		# eat the 'e'
	return(\%d);
    } elsif ($c eq 'l') {
	# list
	$$pref++;		# eat the 'l'
	my @l = ();
	while (substr($data, $$pref, 1) ne 'e') {
	    push(@l, bdecodefile($data, $pref));
	    if ($_btdead)  {
		undef($_btdead);
		return 0;
	    }
	}
	$$pref++;		# eat the 'e'
	return(\@l);
    } elsif ($c eq 'i') {
	if (substr($data, $$pref) =~ /^i(\d+)e/s) {
	    # number
	    $$pref += length($1) + 2;
	    return($1);
	} else { $_btdead = 1; return 0; }
    } else {
	# data buffer with length $len
	if (my($len, $dat) = (substr($data, $$pref) =~ /^(\d+):(.*)/s)) {
	    my $dlen = length($dat);
	    if ($len > $dlen) { $_btdead = 1; return 0; }
	    $$pref += length($len) + 1;	# move past length field + ':'
	    my $buf = substr($data, $$pref, $len);
	    $$pref += $len;	# move past data buffer
	    return($buf);
	} else { $_btdead = 1; return 0; }
    }
}
#####################################
# bdecode chunk
#####################################
sub _bdecode_chunk {
	my ( $q, $r ); # can't declare 'em inline because of qr//-as-closure
	my $str_rx = qr/ \G ( 0 | [1-9] \d* ) : ( (??{
		# workaround: can't use quantifies > 32766 in patterns,
		# so for eg. 65536 chars produce something like '(?s).{32766}.{32766}.{4}'
		$q = int( $^N \/ 32766 );
		$r = $^N % 32766;
		$q--, $r += 32766 if $q and not $r;
		"(?s)" . ( ".{32766}" x $q ) . ".{$r}"
	}) ) /x;

	if( m/$str_rx/xgc ) {
		return $2;
	}
	elsif( m/ \G i ( 0 | -? [1-9] \d* ) e /xgc ) {
		return $1;
	}
	elsif( m/ \G l /xgc ) {
		my @list;
		until( m/ \G e /xgc ) {
			push @list, _bdecode_chunk();
		}
		return \@list;
	}
	elsif( m/ \G d /xgc ) {
		my $last_key;
		my %hash;
		until( m/ \G e /xgc ) {
			m/$str_rx/xgc;

			my $key = $2;

			$last_key = $key;
			return 0 if ($bemustdie);
			$hash{ $key } = _bdecode_chunk();
		}
		return \%hash;
	}
	else {
		$bemustdie = 1;
	}
}
##########################################
# bdecode file
#########################################
sub bdecode {
	local $_ = shift;
	$bemustdie = 0;
	my $data = _bdecode_chunk();
	return $data;
}
# 遍历torrent文件，分析保存
my @torrent_file=`find $torrent_dir -type f`;
chomp(@torrent_file);

foreach my $file(@torrent_file)
{
	my $cmd="$dumptorrent_cmd -v $file > $tmp_file";
	system("$cmd");
	my $info_hash=`cat $tmp_file|grep 'Info Hash' | awk -F : '{print \$2}' | sed -r 's/^\\s+//'`;
	chomp($info_hash);
	my $creation_date=`cat $tmp_file|grep 'Creation Date' | sed -r 's/Creation Date:\\s+//'`;
	chomp($creation_date);
	# 获取文件列表
	my $result_file=`cat $tmp_file | grep -A 1000 'Files:' | grep -B 1000 'Announce List:'`;
	chomp($result_file);
	my $files="";
	if($result_file eq "")		# 没有Announce List
	{
		$files=`cat $tmp_file | grep -A 1000 'Files:' | sed  '1d' | sed -r 's/^\\s+//'`;
	}
	else					# 存在Announce List
	{
		$files=`cat $tmp_file | grep -A 1000 'Files:' | grep -B 1000 'Announce List:'| sed  '1d' | sed '\$d'| sed -r 's/^\\s+//'`;
	}
	chomp($files);
	my $size=`cat $tmp_file |grep 'Size' | sed -r 's/Size:\\s+//' | awk -F '(' '{print \$2}' | sed -r 's/\\)//'`;
	chomp($size);
	my $name=`cat $tmp_file|grep 'Name' | sed -r 's/^Name:\\s+//'`;
	chomp($name);

	
	# 更新 torrent 的announce url
	#open(FIX,$file) || print "Unable to read $file";
	#my $decode = modify(join('',<FIX>));
	#close(FIX);
	#if ($decode) 
	#{
	#	open(NEW,"> $file") || print "Unable to write to $file";
	#	print NEW $decode;
	#	close(NEW);
	#}
	# 根据torrent的创建时间来建立保存torrent目录
	my $dir_date=`date -d "$creation_date" +\%Y-\%m`;
	chomp($dir_date);
	my $download_dir="$download_torrent_dir/$dir_date";
	system("mkdir -p $download_dir");
	$cmd="mv $file $download_dir";
	system("$cmd");

	# 更新 torrent db文件，保存已经分析修改过的torrent文件
	Updb("$info_hash","NEW");
	
	# torrent 文件创建时间
	my $key=$info_hash."_createdate";
	Updb("$key","$creation_date");

	# 保存创建时间字符窜，方便后面进行排序和生成模板
	my $time=`date -d "$creation_date" +\%s`;
	chomp($time);
	$key=$info_hash."_time";
	Updb("$key","$time");
	
	# torrent 文件列表
	$key=$info_hash."_filelist";
	Updb("$key","$files");
	
	# torrent 文件大小
	$key=$info_hash."_size";
	Updb("$key","$size");

	# torrent 经过修改后的保存目录
	$key=$info_hash."_dir";
	Updb("$key","$dir_date");
	
	# torrent 种子文件名称
	$key=$info_hash."_name";
	Updb("$key","$name");
}
