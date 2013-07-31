<?
// +--------------------------------------------------------------------------+
// | Project:    CMS BT MODULE                                    	      |
// | Function : Scrape Torrent File					      |
// +--------------------------------------------------------------------------+
// | Change log                                                               |^M
// | 1. 修改tracker scrape 超时问题                                           |^M
// | Function : Parse Torrent File                                            |^M

// setting include path
//$cur_dir=getcwd();
$cur_dir = dirname(__FILE__);
chdir($cur_dir);
/*$path = ini_get('include_path');
ini_set("include_path", "$cur_dir:$path");
$path = ini_get('include_path');
echo $path;
*/

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

/* tracker 更新状态值 scrape_status 默认值  OK  (TIMEOUT) */
$scrape_status="OK";

/* torrent file update interval second*/
$torrent_update_interval = 3600 ; 

// get torrent file dir
function Get_Torrent($id,$datatime)
{
	global $torrent_dir;
    // save torrent to local file 
	$day_dir = date('Y-m-d',strtotime("$datatime"));
	$save_as="$torrent_dir/$day_dir/$id.torrent";
    return $save_as;
}


// update seeder and leecher into database
function update_database($torrentfile,$id)
{

    global $dbtbpre,$empire,$error_msg,$scrape_status;
	$TorrentInfo = array();
    $TorrentInfo = ParseTorrent($torrentfile);
    $announce = strtolower($TorrentInfo[0]);
    $infohash = $TorrentInfo[1];
    $annlist = $TorrentInfo[6];
    $total_seeders=0;
    $total_leechers=0;
    $total_completed=0;
    //echo "error_msg_int =======$error_msg\n";
    $error_msg="";
    $scrape_status="OK";
   //echo "infohash=$infohash\n";
   //echo "announce=$announce\n";
    //EXTERNAL SCRAPE
    if(!isset($annlist))
    {
        //echo "single ---annlist\n";
	    $tracker=str_replace("/announce","/scrape",$announce);
	    $stats          = torrent_scrape_url($tracker, $infohash);
	    
	    $seeders        = strip_tags($stats['seeds']);
	    $leechers       = strip_tags($stats['peers']);
	    $downloaded     = strip_tags($stats['downloaded']);
	    $total_seeders = $seeders;
	    $total_leechers =  $leechers;
	    $total_completed = $downloaded;
    
    }
    else
    {
	    //echo "multi-----annlist";
	    foreach ($annlist as $key => $value)
	    {
	       foreach($value as $key1 => $value1)
	       {

		    $tracker=str_replace("/announce","/scrape",$value1);	
		    $stats 			= torrent_scrape_url($tracker, $infohash);
		    $seeders 		= strip_tags($stats['seeds']);
		    $leechers 		= strip_tags($stats['peers']);
		    $downloaded 	= strip_tags($stats['downloaded']);

		    $total_seeders=$total_seeders + $seeders;
    	    $total_leechers=$total_leechers + $leechers;
    		$total_completed=$total_completed + $downloaded;
	       }
	    }
    }
    //echo "scrape after======$error_msg\n"; 
    if(preg_match("/Connection timed out/i","$error_msg") || preg_match("/No such file or directory/i","$error_msg") || preg_match("/Connection refused/i","$error_msg") || preg_match("/HTTP request failed/i","$error_msg") ||  preg_match("/getaddrinfo failed/i","$error_msg"))
    {
	$scrape_status="TIMEOUT";	
    } 
    //echo "update database............\n";
    if ($total_seeders <= 0 )
    {
    $cmd_sql= ("update {$dbtbpre}ecms_torrent set seeders=0,leechers=0,times_completed=0,scrape_status='$scrape_status',last_action='".get_date_time()."' where id=$id");
    }
    else
    {
	$cmd_sql= ("update {$dbtbpre}ecms_torrent set seeders=$total_seeders,leechers=$total_leechers,times_completed=$total_completed,scrape_status='$scrape_status',last_action='".get_date_time()."' where id=$id");
    }	
    //echo "execute==$cmd_sql\n";
    $ret=$empire->query1($cmd_sql);    
    if (!$ret) 
    {
        return 1;
    }
    
}

// main prog
// read url from database and save to file 

$link=db_connect();
$empire=new mysqlquery();
global $dbtbpre;
// 取出60分钟没有更新的种子文件 (2700 second)
#$query="select id,newstime,last_action from {$dbtbpre}ecms_torrent where checked=1 and UNIX_TIMESTAMP(now())-UNIX_TIMESTAMP(last_action) >$torrent_update_interval and (scrape_status='' or scrape_status='$scrape_status') order by last_action limit 500";
$query="select id,newstime,last_action from {$dbtbpre}ecms_torrent where checked=1 and UNIX_TIMESTAMP(now())-UNIX_TIMESTAMP(last_action) >$torrent_update_interval and (scrape_status='' or scrape_status='$scrape_status') order by RAND() limit 1500";
#$query="select id,newstime from {$dbtbpre}ecms_torrent where checked=1 and id=497";
//echo "$query\n";
$sql=$empire->query($query);
while($r=$empire->fetch($sql))
{
	$torrent_file=Get_Torrent($r['id'],$r['newstime']);
	if (is_file($torrent_file) && is_readable($torrent_file))
	{
	    echo "Current Processing Id ====== ".$r['id']."\n";
	    update_database($torrent_file,$r['id']);
    	}
    	else
    	{
		echo "Current Processing Id ====== ".$r['id']."=====Error==NOT FOUND Torrent File\n";
    	}
}

db_close();
$empire=null;

?>
