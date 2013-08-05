#! /usr/bin/perl
use Cwd;
$| = 1;
# 0=no debug, 1=display progress, 2=complete dump
$DEBUG = 1;  		

if(scalar(@ARGV) < 1)
{
	print "Usage: $0 <fully-qualified-URL> <search-phrase>\n";
	exit 1;
}

# Initialize.
%URLqueue = ();
$been = 0;
$search_phrase = $ARGV[1];
my $agent="Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 2.0.50727; MAXTHON 2.0)";

# Load the queue with the first URL to hit.
$URLqueue{$ARGV[0]} = 0;
$thisURL = &find_new(%URLqueue);

# While there's a URL in our queue which we haven't looked at ...
my $listen_port=6800;
my $cachedir = cwd . "/CACHE/";
system("mkdir -p  $cachedir");
system("find $cachedir  -size 0 -exec rm -fr {} \\;");

while($thisURL ne "")
{

	# Progress report.
	$count=scalar(keys(%URLqueue));

	print "-----------------------------------------\n" if($DEBUG>=1);
	printf("Been: %d  To Go: %d\n", $been, $count-$been)if($DEBUG>=1);
	print "Current URL: $thisURL\n" if($DEBUG>=1);
	&dump_stack() if($DEBUG>=2);

	# Split the protocol from the URL.
	($protocol, $rest) = $thisURL =~ m|^([^:/]*):(.*)$|;

	# Split out the hostname, port and document.
	($server_host, $port, $document) = $rest =~ m|^//([^:/]*):*([0-9]*)/*([^:]*)$|;
	#print "document : $document\n";
	# Get the page of text and remove CR/LF characters and HTML
	# comments from it.
	#$page_text = &get_http($client_host, $server_host, $port, $document);
	my $cache_key=`echo "$thisURL"|md5sum | awk '{print \$1}'`;
	chomp($cache_key);
	my $html_file=$cachedir.$cache_key;	
	if ( ! -e $html_file )
	{
		$cmd="wget -t 2 --timeout=5 --user-agent=\"$agent\" -o /tmp/wget.log -O $html_file \"$thisURL\"";
		system($cmd);
	}
	$page_text = `cat $html_file`;
	chomp($page_text);
	#$page_text =~ tr/\r\n//d;
	$page_text =~ s|<!--[^>]*-->||g;

	# process text for special block
	if( $thisURL =~ m/(other|microsoft|certification-central|business-and-investing|professional-and-technical|graphic-design|magazine|networking|web-development|database|hardware|software|programming|operating-system|internet)\/(.*)-(\d+)\.html$/ ) 
	{
		#print "$1 : $thisURL\n";
		#my $release=`sed -n '/^<img/,/<center>/p' /tmp/tmp.html | sed 1,2d | sed '\$d'`;
		my $category=$1;
		#my $book_name = $2;
		my $download_id=$3;
		#if( $page_text =~ m/<img src="(.*)"\s+alt=".*"\s+.*>/i )
		#{
		#	print $1;
		#}
		#my $info = $page_text =~ m/^\w+\s+:/;
		#my $release = $page_text =~ m/Unpack/;
		my $torrent_url=$protocol."://".$server_host."/download.php?id=".$download_id;
		my $torrent_key=`echo "$torrent_url"|md5sum | awk '{print \$1}'`;
        	chomp($torrent_key);
        	my $torrent_file=$cachedir.$torrent_key;
        	if ( ! -e $torrent_file )
		{
			$cmd="wget -t 2 --timeout=5 --user-agent=\"$agent\" -o /tmp/wget.log -O $torrent_file $torrent_url";
        		system($cmd);
		}
		my $ebook_root_dir="/mnt/win_d/ebook/";
		my $this_book_dir=$ebook_root_dir.$category;
		system("mkdir -p $this_book_dir");
		#downlad this torrent
		my $download_log="/tmp/$listen_port.log";
	$cmd="aria2c -d $this_book_dir --seed-time=0 --listen-port=$listen_port -D -T $torrent_file >$download_log 2>&1";
		while(1)
		{
			my $bt_count=`ps axf | grep "aria2c" | grep -v grep| wc -l`;
			chomp($bt_count);
			printf("aria2c count : %d \n", $bt_count)if($DEBUG>=1);

			if ($bt_count >= 50 )
			{
				sleep 240;
				&kill_aria2c();
			}
			else
			{
				last;
			}
		}
		system($cmd);
		$listen_port+=1;
		
	}
	
	# Find anchors in the HTML and update our list of URLs..
	#@anchors = $page_text =~ m|<A\s+HREF="(.*?)"|gi;
	@anchors = $page_text =~ m|<A\s+HREF=['"](.*?)['"]|gi;
	foreach $anchor (@anchors)
	{
		# exclude javascript from url 
		if ( $anchor =~ m/javascript/i ) {next;}
		# exclude # from url
		if ( $anchor =~ m/^#$/ ) { next;}
		$newURL=&fqURL($thisURL,$anchor);

		if($URLqueue{$newURL} > 0)
		{
			# Increment the count for URLs we've already 
			# checked out.
			$URLqueue{$newURL}++;
		}
		else
		{

			# Add a zero record for URLs we haven't 
			# encountered.
			# Optionally, ignore URL's which point to other
			# hosts.
			($new_host) = $newURL =~ m|^[^:/]*:/*([^/:]*):*[0-9]*/*[^:]*$|;
			if( $new_host eq $server_host)
			{
				$URLqueue{$newURL}=0;
			}
		}
	}
	# Record the fact that we've been here, and get a new URL to process.
	$URLqueue{$thisURL} ++;
	$been ++;
	$thisURL = &find_new(%URLqueue);
}
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
# Do a linear search of the URL stack to find a URL with a data
# value of 0 (i.e. one we haven't checked out yet).
#---------------------------------------------------------------
sub find_new
{
	local(%URLqueue) = @_;
	local($key, $value);

	while(($key, $value) = each(%URLqueue))
	{
		return $key if($value == 0);
	}
	return "";
}

#-------------------------------------------------------------------
# Debugging utility.
#-------------------------------------------------------------------
sub dump_stack
{
	local($key, $x);
	local($done, $togo) = ("", "");

	foreach $key (keys(%URLqueue))
	{
		if($URLqueue{$key} == 0)
		{
			$togo .= "  " . $key . "\n";
		}
		else
		{
			$done .= "  " . $key . " (hitcount = " . $URLqueue{$key} . ")\n";
		}
	}

	print "Been There:\n" . $done;
	print "To Go:\n" . $togo;
	print "------- Hit Q to Quit, Enter to Continue -------\n";
	read(STDIN, $key, 1);
	exit(1) if($key eq 'Q' || $key eq 'q');
}

#-------------------------------------------------------------------
## kill aria2c 
##-------------------------------------------------------------------
#
sub kill_aria2c
{
	my @log_id=`grep  "exception: Failed to send data" /tmp/*.log |sort -u| awk -F ":" '{print \$1}' | sed -r 's#/tmp/##g'| sed -r 's#\.log\$##g'`;
	chomp(@log_id);
	foreach my $id (@log_id)
	{
		my $aria2c_id=` ps axf  | grep aria2c | grep -v grep | grep "listen-port=$id" | awk '{print \$1}'`;
		chomp($aria2c_id);
		if ( "$aria2c_id" != "")
		{
			system("kill  $aria2c_id");
		}
	}
}
