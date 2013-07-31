<?
/*
// +--------------------------------------------------------------------------+
// | Project:    BT CMS - BT for CMS                                		  |
*/

/* ECMS include heaser */
require("../class/connect.php");
include("../class/config.php");
include("../class/db_sql.php");

/* BT BENC header */
require_once("include/benc.php");
$max_torrent_size="819200";
$temp_file = tempnam(sys_get_temp_dir(), 'Tux');
$torrent_dir = "../../torrent";    /*  root dir */

// Returns the current time in GMT in MySQL compatible format.
function get_date_time($timestamp = 0)
{
  if ($timestamp)
    return date("Y-m-d H:i:s", $timestamp);
  else
    return gmdate("Y-m-d H:i:s");
}

function sqlesc($x) {
    return "'".mysql_real_escape_string($x)."'";
}


/* error msg print and return 1 */
function halt($msg)
{
    print ("$msg");
    return 1;
}

/* get torrent file url form database and save to local */
function Get_Torrent($url,$temp_file)
{

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
    $fp = fopen("$temp_file", "w");
    if ($fp)
    {
	        @fwrite($fp, $file_contents, strlen($file_contents));
		    fclose($fp);
    }
}


function dict_check($d, $s) {
        if ($d["type"] != "dictionary")
                halt("not a dictionary");
        $a = explode(":", $s);
        $dd = $d["value"];
        $ret = array();
        foreach ($a as $k) {
                unset($t);
                if (preg_match('/^(.*)\((.*)\)$/', $k, $m)) {
                        $k = $m[1];
                        $t = $m[2];
                }
                if (!isset($dd[$k]))
                        halt("dictionary is missing key(s)");
                if (isset($t)) {
                        if ($dd[$k]["type"] != $t)
                                halt("invalid entry in dictionary");
                        $ret[] = $dd[$k]["value"];
                }
                else
                        $ret[] = $dd[$k];
        }
        return $ret;
}

function dict_get($d, $k, $t) {
        if ($d["type"] != "dictionary")
                halt("not a dictionary");
        $dd = $d["value"];
        if (!isset($dd[$k]))
                return;
        $v = $dd[$k];
        if ($v["type"] != $t)
                halt("invalid dictionary entry type");
        return $v["value"];
}

/* read tmpfile and  modify ,save to torrent */

function Save_Torrent($tmpfile,$id,$datatime)
{
	global $max_torrent_size,$dbtbpre,$empire,$torrent_dir;
	$dict = bdec_file($tmpfile, $max_torrent_size);
    if (!isset($dict))
    {
        halt("file type wrong, This is not a bencoded file!");
    }
	list($ann, $info) = dict_check($dict, "announce(string):info");
    list($dname, $plen, $pieces) = dict_check($info, "name(string):piece length(integer):pieces(string)");
    if (strlen($pieces) % 20 != 0)
    {
        halt("pieces file type wrong, This is not a bencoded file!");
    }
    
    $filelist = array();
    $totallen = dict_get($info, "length", "integer");
    if (isset($totallen)) 
    {
        $filelist[] = array($dname, $totallen);
        $type = "single";
    }
    else 
    {
        $flist = dict_get($info, "files", "list");
        if (!isset($flist))
                halt("missing both length and files");
        if (!count($flist))
                halt("no files");
        $totallen = 0;
        foreach ($flist as $fn) {
                list($ll, $ff) = dict_check($fn, "length(integer):path(list)");
                $totallen += $ll;
                $ffa = array();
                foreach ($ff as $ffe) {
                        if ($ffe["type"] != "string")
                                halt("filename error");
                        $ffa[] = $ffe["value"];
                }
                if (!count($ffa))
                        halt("filename error");
                $ffe = implode("/", $ffa);
                $filelist[] = array($ffe, $ll);
        
        }
        $type = "multi";
    }
    
    
    unset($dict['value']['info']['value']['crc32']); // remove crc32
    unset($dict['value']['info']['value']['ed2k']); // remove ed2k
    unset($dict['value']['info']['value']['md5sum']); // remove md5sum
    unset($dict['value']['info']['value']['sha1']); // remove sha1
    unset($dict['value']['info']['value']['tiger']); // remove tiger
    unset($dict['value']['azureus_properties']); // remove azureus properties
    $dict=bdec(benc($dict)); // double up on the becoding solves the occassional misgenerated infohash
    list($ann, $info) = dict_check($dict, "announce(string):info");

    $infohash = pack("H*", sha1($info["string"]));
    $infohash= urlencode($infohash);
        
    $cmd_sql= ("update {$dbtbpre}ecms_torrent set info_hash='$infohash',numfiles='".count($filelist)."',last_action='".get_date_time()."' where id=$id");
    echo "$cmd_sql\n";
    /* $ret=$empire->fetch1($cmd_sql);    
     if (!$ret) 
     {
        if (mysql_errno() == 1062)
                halt("torrent already uploaded!");
        halt("mysql puked: ".mysql_error());
    }
*/
    #$cmd_sql="DELETE FROM files WHERE torrent = $id";
    #echo "$cmd_sql\n";
    /*$empire->fetch1($cmd_sql);
    foreach ($filelist as $file) 
    {
            $cmd_sql="INSERT INTO files (torrent, filename, size) VALUES ($id, ".sqlesc($file[0]).",".$file[1].")";
            @$empire->fetch1($cmd_sql);
    }*/  
	// save torrent to local file 
	$day_dir = date('Y-m-d',strtotime("$datatime"));
	if(!is_dir("$torrent_dir/$day_dir"))
	{
        mkdir("$torrent_dir/$day_dir",0777,true);
	}
	$fp = fopen("$torrent_dir/$day_dir/$id.torrent", "w");
    if ($fp)
    {
            @fwrite($fp, benc($dict), strlen(benc($dict)));
            fclose($fp);
    }
	
}


/* read url from database and save to file */

$link=db_connect();
$empire=new mysqlquery();
global $dbtbpre;
$r=$empire->fetch1("select id,newstime,downpath from {$dbtbpre}ecms_torrent limit 1");
$path_r=explode("\r\n",$r['downpath']);
$showdown_r=explode("::::::",$path_r[0]);
$torrent_url=$showdown_r[1];

Get_Torrent($torrent_url,$temp_file);

#echo $temp_file;
Save_Torrent($temp_file,$r['id'],$r['newstime']);

db_close();
$empire=null;
?>
