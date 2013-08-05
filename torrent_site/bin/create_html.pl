#!/usr/bin/perl
#************************************************************************************************************#
# ScriptName:           analyse_torrent.pl 
# Author:               hua.fu <hua.fu@alibaba-inc.com>            
# Date:                 2010-03-29                 
# Modify Author:        Hua.fu <hua.fu@alibaba-inc.com> 
# Modify Date:          2010-03-29            
# Function:             分析torrent种子文件         
#************************************************************************************************************# 
use BerkeleyDB;
use HTML::Template;
use strict;
#Debug using Data::Dumper
use Data::Dumper;
#
use Cwd 'abs_path';
my $abs_path = abs_path($0);
my $base_dir=`dirname $abs_path`;
chomp($base_dir);
chdir($base_dir);
my $torrent_dbfile="../data/bdb/torrent.bdb";
my $tmp_file="/tmp/tmp_bitfile";
my $dumptorrent_cmd="./dumptorrent";
# 下载的torrent 目录(web服务器目录,相对document_root目录)
my $download_torrent_dir="/torrent";
my $create_html_dir="../web_root";
my $template_dir="../template";
my $stop_word_file="$base_dir/stop_terms.txt";
my $static_html_dir="/all-torrent-index";
# 保存要生成的torrent list 哈希表
my %torrent_hash=();
my $db = new BerkeleyDB::Hash
-Filename => $torrent_dbfile,
-Flags    => DB_CREATE
        or die "Cannot open file $torrent_dbfile: $! $BerkeleyDB::Error\n";

my @loop_data=();   # torrent 记录
my @page_data=();   # 页面导航
# 每页40条
my $torrent_per_page = 40;

my $torrent_count = 0;
my $torrent_page_no = 1;
my $record_all = 0;
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
# 查找最新更新生成模板的种子文件
# 每次只取出20条最新的种子文件
#####################################
sub find_new()
{
	my $count=1;
	my ($k, $v) = ("", "") ;
	my $cursor = $db->db_cursor();
	while ($cursor->c_get($k, $v, DB_NEXT) == 0)
	{ 
		if($count == 21 ) { last;}
		if($v eq "NEW")	
		{		
			$torrent_hash{$k}="0";
			$count ++;
		}
	}
	undef $cursor;
}

#####################################
# 重新生成已经生成过的种子文件网页
#####################################
sub find_already()
{
	my ($k, $v) = ("", "") ;
	my $cursor = $db->db_cursor();
	while ($cursor->c_get($k, $v, DB_NEXT) == 0)
	{ 
		if($k =~ m/^[a-zA-Z0-9]+$/)
		{
			if ( $v eq "ALREADY")
			{
				$torrent_hash{$k}="$v";
			}
		}
	}
	undef $cursor;
}

#####################################
# stopword file process
#####################################
sub ignore_terms {
  my @stopwords;
  my $stopwords_regex;
  open (FILE, $stop_word_file) or (warn "Cannot open $stop_word_file: $!");
  while (<FILE>) 
  {
	  chomp;
	  $_ =~ s/\#.*$//g;
	  $_ =~ s/\s//g;
	  next if /^\s*$/;
	  $_ =~ s/([^\w\s])/\\$1/g;
	  push @stopwords, $_;
  }
  close(FILE);
  $stopwords_regex = '(' . join('|', @stopwords) . ')';
  return $stopwords_regex;
}

#####################################
# 根据文档内容生成keyword
#####################################
sub create_keyword
{
	my $MIN_TERM_LENGTH=5;		# 关键字最短字符
	my $contents=shift;
	my %terms;
	my @return_keyword=();
  	$contents =~ s/(<[^>]*>)|(&nbsp;)|(&#160;)/ /gs;              # remove html poorly
  	$contents =~ s/^\s+//gs;
  	$contents =~ s/\s+$//gs;
  	$contents =~ s/\(|\)//gs;
  	$contents =~ s/\s+/ /gs;

	$contents = lc($contents);
	#print "Debug =====\n $contents\n";
	my $stopwords_regex = ignore_terms();

	my @word=split(/\s+/,$contents);
	foreach my $term(@word)
	{
		my $domain_regex="^[www]?.*\.[com|net]\$";
		next if $term =~ m/$domain_regex/io;
		next if $term =~ m/^$stopwords_regex$/io;                   # skip stop words
		if (length $term >= $MIN_TERM_LENGTH ) 
		{ 
			$terms{$term} = $terms{$term} +1 ;
		}
	}
	#print Dumper(\%terms);
	my $count=1;
	for my $key_word ( sort { $terms{$b} <=> $terms{$a} } keys %terms)
	{
		if ( $count == 30 ) { last; }
		#print "key= $key_word val=$terms{$key_word}\n";
		push(@return_keyword,$key_word);
		$count= $count +1;
	}	
	my $return_str = join(' ',@return_keyword);	
	#print "Debug =  \n $return_str \n";
	return $return_str;
}
#####################################
# 根据种子重新生成种子索引html列表
#####################################
sub create_html_index()
{
	my $page_no=shift;
	my $row_data=shift;
	my $nav_data=shift;
	my $keyword_content=shift;
	print "Create Index html PageNum = $page_no\n";
	my @loop_data=@{$row_data};
	my @page_data=@{$nav_data};
	# 调用模板文件
	my $template_file = "";
	my $index_file_name="";
	my $page_title="";
	if($page_no == 1) 
	{ 
		$template_file = "$template_dir/index.html";
		$index_file_name = "/index.html";
	}
	else 
	{ 	
		$template_file = "$template_dir/list.html"; 
		$index_file_name="$static_html_dir/all-torrent-index-page$page_no.html";
	}
	my $template = HTML::Template->new(filename => "$template_file");
	$template->param(DATA_LOOP => \@loop_data);
	$template->param(PAGE_LOOP => \@page_data);
	$template->param(total_count => $record_all);
	my $html_file="$create_html_dir"."$index_file_name";
	# 根据文件内容生成关键字列表
	if($page_no != 1)
	{
		my $key_word=create_keyword($keyword_content);
		$template->param(keyword =>"$key_word");
		$template->param(page_no =>"$page_no");
	}
	my $file_content = $template->output;
	open(NEW,"> $html_file") || print "Unable to write to $html_file";
	print NEW $file_content;
	close(NEW);
}

#####################################
# 生成页面导航(共有多少记录，多少页面)
#####################################
sub create_page_nav()
{
	my $curent_page_no=shift;
	my $record_all=shift;
	# calculate number of pages needing links
	my $pages_count="";;
	my $pages="";
	if($record_all > $torrent_per_page )
	{
		$pages_count=int($record_all/$torrent_per_page)+1
	}
	elsif($record_all <= $torrent_per_page)
	{
		$pages_count=1;
	}
	# 导航栏，每页只显示20个导航,以当前page为标准，前后各显示10个页面导航连接
	my $nav_count_end="17";
	my $nav_count_start="1";
	if( $curent_page_no + 8 < $pages_count ) 
	{ $nav_count_end= $curent_page_no + 8;}
	else 
	{ $nav_count_end = $pages_count ; }

	if( $curent_page_no - 8 > 0 ) 
	{ $nav_count_start = $curent_page_no - 8;}

	if ( $nav_count_end < 17 ) 
	{ $nav_count_end =17 ;}
	elsif ( $pages_count == $nav_count_end && $nav_count_end - $nav_count_start < 17 )
	{ $nav_count_start = $nav_count_end - 17 ;}

	#for(my $page_count=1;$page_count<=$pages_count;$page_count++)
	for(my $page_count=$nav_count_start;$page_count<=$nav_count_end;$page_count++)
	{
		my $href="";
		if($page_count == 1) { $href = "/index.html" ;}
		else { $href="$static_html_dir/all-torrent-index-page$page_count.html"; }
		my %row_data;  # 每一行数据             
		if ($curent_page_no == $page_count  )
		{
			$row_data{page_href} = " <span class=current>$page_count</span>";
		}
		else
		{
			$row_data{page_href} = "<a  href=$href>$page_count</a>";
		}
		push(@page_data, \%row_data);
	}

}
#####################################
# 生成网页,每次首页40条是最新更新的
#####################################

&find_new();			# 最新加入的20条

&find_already();		# 已有的所有数据

#print Dumper(\%torrent_hash);
#exit 0;

#######################################################
# 按照torrent创建时间进行排序生成,把最新的排序在最前面
# ####################################################
$record_all = scalar(keys(%torrent_hash));
my $keyword_content="";			# 保存当页的关键字列表		 
for my $info_hash ( sort { $torrent_hash{$a} <=> $torrent_hash{$b} } keys %torrent_hash) 
{
	#print "$info_hash = $torrent_hash{$info_hash}\n"; 
	#读取torrent信息从db文件，生成html静态文件

	my $key=$info_hash."_createdate";
	my $creation_date = DbGet($key);
	chomp($creation_date);

	$key=$info_hash."_filelist";
	my $files = DbGet($key);

	$key=$info_hash."_size";
	my $size = DbGet($key);
	chomp($size);

	$key=$info_hash."_dir";
	my $dir_date = DbGet($key);
	#my $download_link="$download_torrent_dir/$dir_date/$info_hash.torrent";

	$key=$info_hash."_name";
	my $name = DbGet($key);
	chomp($name);
	#print "Debug == Name Before = $name\n";
	$name =~ s/\./ /g;
	# 去掉ebook- 类似标记
	if($name =~ s/Ebook-.*$//gi) { $name="Ebook - $name";}
	#print "Debug == Name After = $name\n";
	my $download_link="/download_captcha/verify_down.php?torrent_name=$name&torrent_dir=$dir_date/$info_hash.torrent";

	my %row_data;  # 每一行数据		
	# fill in this row
	$row_data{torrent_name} = "$name";
	$row_data{torrent_size} = "$size";
	my $torrent_create_time = `date -d "$creation_date" +\%m/\%d/\%Y`;
	chomp($torrent_create_time);
	$row_data{torrent_add} = "$torrent_create_time";
	$row_data{download_link} = "$download_link";
	if($torrent_count%2 == 0) { $row_data{row_color} = "trkOdd";}
	else { $row_data{row_color} = "trkEven";}

	# 保存keyword生成列表
	$keyword_content= "$keyword_content $name "; 
	# 生成种子文件列表提示
	$files =~ s/\n/<br>/g;
	my $title="Torrent FileList | $files";
	$row_data{filelist} = "$title";
	push(@loop_data, \%row_data);
	# 更新状态到已经生成过的状态
	Updb("$info_hash","ALREADY");
	# 更新每页记录的计数器
	$torrent_count= $torrent_count + 1 ;
	if($torrent_count == $torrent_per_page )
	{
		&create_page_nav($torrent_page_no,$record_all);
		&create_html_index($torrent_page_no,\@loop_data,\@page_data,$keyword_content);
		# 更新 页面索引数
		$torrent_page_no = $torrent_page_no + 1;
		# 将每页记录计数器清零
		$torrent_count = 0 ;
		# 清空loop_data 
		@loop_data=();
		# 清空page_data
		@page_data=();
		# 清空keyword 
		$keyword_content="";
	}
}

if(scalar(@loop_data) ne '0')	# 不够 40条记录或者 最后一页
{
	&create_page_nav($torrent_page_no,$record_all);
        &create_html_index($torrent_page_no,\@loop_data,\@page_data,$keyword_content);
}
print "Record Count =  $record_all\n";
#########################################

