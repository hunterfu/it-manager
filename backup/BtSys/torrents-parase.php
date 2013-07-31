<?
// +--------------------------------------------------------------------------+
// | Project:    CMS BT MODULE                                    	      |
// | Function : Parse Torrent File					      |
// +--------------------------------------------------------------------------+
// | Change log 					      		      |
// | 1. 修改tracker scrape 超时问题					      |
// | Function : Parse Torrent File					      |

/* ECMS include heaser */
require("../class/connect.php");
include("../class/config.php");
include("../class/db_sql.php");

/* BT BENC header */
require_once("btinclude/parse.php");
require_once("btinclude/common.php");

/* torrent tmp file name */
$temp_file = tempnam(sys_get_temp_dir(), 'Tux');
/* torrent file save dir final*/
$torrent_dir = "../../torrent";   
$down_torrent_dir = "/torrent";

// match domain
function isValidDomain($domainName) 
{ 
	return ereg("^(http|ftp|https)://.*$", $domainName); 
}
// calculator file size float
function mksize($bytes)
{
        if ($bytes < 1000 * 1024)
                return number_format($bytes / 1024, 2) . " kB";
        elseif ($bytes < 1000 * 1048576)
                return number_format($bytes / 1048576, 2) . " MB";
        elseif ($bytes < 1000 * 1073741824)
                return number_format($bytes / 1073741824, 2) . " GB";
        else
                return number_format($bytes / 1099511627776, 2) . " TB";
}

// calculator file size int
function mksizeint($bytes)
{
        $bytes = max(0, $bytes);
        if ($bytes < 1000)
                return floor($bytes) . " B";
        elseif ($bytes < 1000 * 1024)
                return floor($bytes / 1024) . " kB";
        elseif ($bytes < 1000 * 1048576)
                return floor($bytes / 1048576) . " MB";
        elseif ($bytes < 1000 * 1073741824)
                return floor($bytes / 1073741824) . " GB";
        else
                return floor($bytes / 1099511627776) . " TB";
}


// get torrent file url form database and save to local 
function Get_Torrent($url,$id,$datatime)
{
	global $torrent_dir;
	if(function_exists('file_get_contents')) 
	{
		$file_contents = file_get_contents($url);
	} 
	else
	{ 
		$ch = curl_init();
		$timeout = 5;
		curl_setopt ($ch, CURLOPT_URL, $url);
		curl_setopt ($ch, CURLOPT_RETURNTRANSFER, 1);
		curl_setopt ($ch, CURLOPT_CONNECTTIMEOUT, $timeout);
		$file_contents = curl_exec($ch);
		curl_close($ch);
    }
    // save torrent to local file 
	$day_dir = date('Y-m-d',strtotime("$datatime"));
	if(!is_dir("$torrent_dir/$day_dir"))
	{
        mkdir("$torrent_dir/$day_dir",0777,true);
	}
	$save_as="$torrent_dir/$day_dir/$id.torrent";
	$fp = fopen("$save_as", "w");
    if ($fp)
    {
	        @fwrite($fp, $file_contents, strlen($file_contents));
		    fclose($fp);
    }
    return $save_as;
}

/* read tmpfile and  modify ,save to torrent */

function Save_Torrent($tmpfile,$id)
{

	global $dbtbpre,$empire;
	$TorrentInfo = array();
    $TorrentInfo = ParseTorrent("$tmpfile");
    $announce = strtolower($TorrentInfo[0]);
    $infohash = $TorrentInfo[1];
    $creationdate = $TorrentInfo[2];
    $internalname = $TorrentInfo[3];
    $torrentsize = $TorrentInfo[4];
    $filecount = $TorrentInfo[5];
    $annlist = $TorrentInfo[6];
    $comment = $TorrentInfo[7];
    $filelist = $TorrentInfo[8];
    $parse_msg = $TorrentInfo[9];
    if ($parse_msg != '')
    {
	echo "problem == $parse_msg\n";
	unlink($tmpfile);
	$cmd_sql="update  {$dbtbpre}ecms_torrent set checked=0 where id=$id";
        @$empire->query1($cmd_sql);
	return 1;
    }
    $torrentsize = mksize($torrentsize);
    $cmd_sql= ("update {$dbtbpre}ecms_torrent set info_hash='$infohash',filesize='$torrentsize',numfiles='$filecount',last_action='".get_date_time()."' where id=$id");
    //echo "$cmd_sql\n";
    $ret=$empire->query1($cmd_sql);    
    if (!$ret) 
    {
        if (mysql_errno() == 1062)
                print ("torrent already uploaded!");
        return 1;
    }
    $cmd_sql="DELETE FROM files WHERE torrent = $id";
    //echo "$cmd_sql\n";
    $empire->query1($cmd_sql);
    if ($filecount == 1)
    {
	//echo "internalname ==$internalname\n";
	//echo "torrentsize == $torrentsize \n";
	$cmd_sql="INSERT INTO files (torrent, filename, size) VALUES ($id,'$internalname','$torrentsize')";
        @$empire->query1($cmd_sql);
    }
    else
    {
    	foreach ($filelist as $file) 
    	{
         	$multiname = $file['path'];//Not needed here really
         	$multitorrentsize = $file['length'];
         	$cmd_sql="INSERT INTO files (torrent, filename, size) VALUES ($id,'$multiname[0]','$multitorrentsize')";
	 	//echo "$cmd_sql\n";
		@$empire->query1($cmd_sql);
    	}	
    }
    return 0;
}

// update downpath to localfile 
function update_downpath($downpath,$id,$torrent_file,$datetime)
{
	global $dbtbpre,$empire,$down_torrent_dir;	
	if(file_exists($torrent_file))
	{	
		$path_r=explode("\r\n",$downpath);
        	$showdown_r=explode("::::::",$path_r[0]);
		$day_dir = date('Y-m-d',strtotime("$datetime"));		
		$save_as="$down_torrent_dir/$day_dir/$id.torrent";
        	$showdown_r[1]=$save_as;
		$path_r=join("::::::",$showdown_r);
		#$new_down=$path_r."\r\n";
		$cmd_sql="update {$dbtbpre}ecms_torrent set downpath='$path_r' where id = $id";
		@$empire->query1($cmd_sql);
	}
}
// read url from database and save to file 

$link=db_connect();
$empire=new mysqlquery();
global $dbtbpre;
$query="select id,newstime,downpath from {$dbtbpre}ecms_torrent where checked=1 and info_hash ='' limit 50000";
$sql=$empire->query($query);
while($r=$empire->fetch($sql))
{
	$path_r=explode("\r\n",$r['downpath']);
	$showdown_r=explode("::::::",$path_r[0]);
	$torrent_url=$showdown_r[1];
	echo "Current Processing Id ====== ".$r['id']."\n";
	if (isValidDomain("$torrent_url"))
	{
		$torrent_file=Get_Torrent($torrent_url,$r['id'],$r['newstime']);
		if (Save_Torrent($torrent_file,$r['id']) == 0)
		{
			update_downpath($r['downpath'],$r['id'],$torrent_file,$r['newstime']);
		}
		else
		{
			echo "Update downpath to Empty\n";
			$cmd_sql="update {$dbtbpre}ecms_torrent set downpath='',checked=0 where id = $id";
                	@$empire->query1($cmd_sql);
		}
	}
	elseif ( $torrent_url == '')
	{
		//   将记录置于未审核状态 
		echo "Error===== DownPath is Empty\n";
		$cmd_sql="update  {$dbtbpre}ecms_torrent set checked=0 where id=".$r['id'];
		@$empire->query1($cmd_sql);

	}
}
db_close();
$empire=null;
?>
