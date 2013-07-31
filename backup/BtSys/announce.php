<?
/*
// +--------------------------------------------------------------------------+
// | Project: CMS BT MODULE                                                   |
// +--------------------------------------------------------------------------+
// | Module: announce.php - Announce File.                                    |
// | Version: 2.5                                                             |
// +--------------------------------------------------------------------------+
*/
//require_once'include/annconf.php';

/* ECMS include heaser */
require("../class/connect.php");
include("../class/config.php");
include("../class/db_sql.php");

/* BT BENC header */
require_once("btinclude/benc.php");
require_once("btinclude/common.php");

/* torrent tmp file name */
$temp_file = tempnam(sys_get_temp_dir(), 'Tux');
/* torrent file save dir final*/
$torrent_dir = "../../torrent";   
$down_torrent_dir = "/torrent";

$announce_interval = 1800;


ob_start("ob_gzhandler");
//
// Begin CrackerTracker  StandAlone
//
$cracktrack = urldecode($_SERVER['QUERY_STRING']);
$wormprotector = array('chr(', 'chr=', 'chr%20', '%20chr', 'wget%20', '%20wget', 'wget(',
                                    'cmd=', '%20cmd', 'cmd%20', 'rush=', '%20rush', 'rush%20',
                                   'union%20', '%20union', 'union(', 'union=', 'echr(', '%20echr', 'echr%20', 'echr=',
                                   'esystem(', 'esystem%20', 'cp%20', '%20cp', 'cp(', 'mdir%20', '%20mdir', 'mdir(',
                                   'mcd%20', 'mrd%20', 'rm%20', '%20mcd', '%20mrd', '%20rm',
                                   'mcd(', 'mrd(', 'rm(', 'mcd=', 'mrd=', 'mv%20', 'rmdir%20', 'mv(', 'rmdir(',
                                   'chmod(', 'chmod%20', '%20chmod', 'chmod(', 'chmod=', 'chown%20', 'chgrp%20', 'chown(', 'chgrp(',
                                   'locate%20', 'grep%20', 'locate(', 'grep(', 'diff%20', 'kill%20', 'kill(', 'killall',
                                   'passwd%20', '%20passwd', 'passwd(', 'telnet%20', 'vi(', 'vi%20',
                                   'insert%20into', 'select%20', 'nigga(', '%20nigga', 'nigga%20', 'fopen', 'fwrite', '%20like', 'like%20',
                                   '$_request', '$_get', '$request', '$get', '.system', 'HTTP_PHP', '&aim', '%20getenv', 'getenv%20',
                                   'new_password', '&icq','/etc/password','/etc/shadow', '/etc/groups', '/etc/gshadow',
                                   'HTTP_USER_AGENT', 'HTTP_HOST', '/bin/ps', 'wget%20', 'uname\x20-a', '/usr/bin/id',
                                   '/bin/echo', '/bin/kill', '/bin/', '/chgrp', '/chown', '/usr/bin', 'g\+\+', 'bin/python',
                                   'bin/tclsh', 'bin/nasm', 'perl%20', 'traceroute%20', 'ping%20', '.pl', '/usr/X11R6/bin/xterm', 'lsof%20',
                                   '/bin/mail', '.conf', 'motd%20', 'HTTP/1.', '.inc.php', 'config.php', 'cgi-', '.eml',
                                   'file\://', 'window.open', '<script>', 'javascript\://','img src', 'img%20src','.jsp','ftp.exe',
                                   'xp_enumdsn', 'xp_availablemedia', 'xp_filelist', 'xp_cmdshell', 'nc.exe', '.htpasswd',
                                   'servlet', '/etc/passwd', 'wwwacl', '~root', '~ftp', '.js', '.jsp', 'admin_', '.history',
                                   'bash_history', '.bash_history', '~nobody', 'server-info', 'server-status', 'reboot%20', 'halt%20',
                                   'powerdown%20', '/home/ftp', '/home/www', 'secure_site, ok', 'chunked', 'org.apache', '/servlet/con',
                                   '<script', '/robot.txt' ,'/perl' ,'mod_gzip_status', 'db_mysql.inc', '.inc', 'select%20from',
                                   'select from', 'drop%20', '.system', 'getenv', 'http_', '_php', 'php_', 'phpinfo()', '<?php', '?>', 'sql=');

$checkworm = str_replace($wormprotector, '*', $cracktrack);

if ($cracktrack != $checkworm)
{
    $cremotead = $_SERVER['REMOTE_ADDR'];
    $cuseragent = $_SERVER['HTTP_USER_AGENT'];

    $fp = fopen ('log.txt', 'a');
    $msg= "Blocked attack from: IP - ".$_SERVER['REMOTE_ADDR']." User Agent - ".$_SERVER['HTTP_USER_AGENT']."\n";
    fwrite ($fp, $msg);
    fclose ($fp);

    die( "Attack detected! <br /><br /><b>Youre attack was blocked:</b><br />$cremotead - $cuseragent" );
}

//
// End CrackerTracker StandAlone
//

// PHP5 with register_long_arrays off?
if (!isset($HTTP_POST_VARS) && isset($_POST))
{
    $HTTP_POST_VARS = $_POST;
    $HTTP_GET_VARS = $_GET;
    $HTTP_SERVER_VARS = $_SERVER;
    $HTTP_COOKIE_VARS = $_COOKIE;
    $HTTP_ENV_VARS = $_ENV;
    $HTTP_POST_FILES = $_FILES;
}


function strip_magic_quotes($arr)
{
    foreach ($arr as $k => $v)
    {
        if (is_array($v))
        { $arr[$k] = strip_magic_quotes($v); }
        else
        { $arr[$k] = stripslashes($v); }
    }

    return $arr;
}

if (get_magic_quotes_gpc())
{
    if (!empty($_GET)) { $_GET = strip_magic_quotes($_GET); }
    if (!empty($_POST)) { $_POST = strip_magic_quotes($_POST); }
    if (!empty($_COOKIE)) { $_COOKIE = strip_magic_quotes($_COOKIE); }
}


// addslashes to vars if magic_quotes_gpc is off
// this is a security precaution to prevent someone
// trying to break out of a SQL statement.
//

if( !get_magic_quotes_gpc() )
{
if( is_array($HTTP_GET_VARS) )
{
while( list($k, $v) = each($HTTP_GET_VARS) )
{
if( is_array($HTTP_GET_VARS[$k]) )
{
while( list($k2, $v2) = each($HTTP_GET_VARS[$k]) )
{
$HTTP_GET_VARS[$k][$k2] = addslashes($v2);
}
@reset($HTTP_GET_VARS[$k]);
}
else
{
$HTTP_GET_VARS[$k] = addslashes($v);
}
}
@reset($HTTP_GET_VARS);
}

if( is_array($HTTP_POST_VARS) )
{
while( list($k, $v) = each($HTTP_POST_VARS) )
{
if( is_array($HTTP_POST_VARS[$k]) )
{
while( list($k2, $v2) = each($HTTP_POST_VARS[$k]) )
{
$HTTP_POST_VARS[$k][$k2] = addslashes($v2);
}
@reset($HTTP_POST_VARS[$k]);
}
else
{
$HTTP_POST_VARS[$k] = addslashes($v);
}
}
@reset($HTTP_POST_VARS);
}

if( is_array($HTTP_COOKIE_VARS) )
{
while( list($k, $v) = each($HTTP_COOKIE_VARS) )
{
if( is_array($HTTP_COOKIE_VARS[$k]) )
{
while( list($k2, $v2) = each($HTTP_COOKIE_VARS[$k]) )
{
$HTTP_COOKIE_VARS[$k][$k2] = addslashes($v2);
}
@reset($HTTP_COOKIE_VARS[$k]);
}
else
{
$HTTP_COOKIE_VARS[$k] = addslashes($v);
}
}
@reset($HTTP_COOKIE_VARS);
}
}


// bittorrent.php integration start
function validip($ip)
{
        if (!empty($ip) && $ip == long2ip(ip2long($ip)))
        {
                // reserved IANA IPv4 addresses
                // http://www.iana.org/assignments/ipv4-address-space
                $reserved_ips = array (
                                array('0.0.0.0','2.255.255.255'),
                                array('10.0.0.0','10.255.255.255'),
                                array('127.0.0.0','127.255.255.255'),
                                array('169.254.0.0','169.254.255.255'),
                                array('172.16.0.0','172.31.255.255'),
                                array('192.0.2.0','192.0.2.255'),
                                array('192.168.0.0','192.168.255.255'),
                                array('255.255.255.0','255.255.255.255')
                );

                foreach ($reserved_ips as $r)
                {
                                $min = ip2long($r[0]);
                                $max = ip2long($r[1]);
                                if ((ip2long($ip) >= $min) && (ip2long($ip) <= $max)) return false;
                }
                return true;
        }
        else return false;
}

// get ip
function getip() {
   if (isset($_SERVER)) {
     if (isset($_SERVER['HTTP_X_FORWARDED_FOR']) && validip($_SERVER['HTTP_X_FORWARDED_FOR'])) {
       $ip = $_SERVER['HTTP_X_FORWARDED_FOR'];
     } elseif (isset($_SERVER['HTTP_CLIENT_IP']) && validip($_SERVER['HTTP_CLIENT_IP'])) {
       $ip = $_SERVER['HTTP_CLIENT_IP'];
     } else {
       $ip = $_SERVER['REMOTE_ADDR'];
     }
   } else {
     if (getenv('HTTP_X_FORWARDED_FOR') && validip(getenv('HTTP_X_FORWARDED_FOR'))) {
       $ip = getenv('HTTP_X_FORWARDED_FOR');
     } elseif (getenv('HTTP_CLIENT_IP') && validip(getenv('HTTP_CLIENT_IP'))) {
       $ip = getenv('HTTP_CLIENT_IP');
     } else {
       $ip = getenv('REMOTE_ADDR');
     }
   }

   return $ip;
 }


// 文件大小
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

function sqlesc($x) {
    return "'".mysql_real_escape_string($x)."'";
}

function gmtime()
{
    return strtotime(get_date_time());
}

function hash_pad($hash) {
    return str_pad($hash, 20);
}

function hash_where($name, $hash) {
    $shhash = preg_replace('/ *$/s', "", $hash);
    return "($name = " . sqlesc($hash) . " OR $name = " . sqlesc($shhash) . ")";
}
/*
function parked()
{
       global $CURUSER;
       if ($CURUSER["parked"] == "yes")
 stderr("Error", "Your account is parked.");
}
*/
// bittorrent.php integration end


function checkconnect($ip,$port)
{
    return (! (@fsockopen($ip, $port, $errno, $errstr, 5))) ? 'no':(@fclose($sockres)?'yes':'yes');
}

function err($msg)
{
        benc_resp(array("failure reason" => array(type => "string", value => $msg)));
        exit();
}

function benc_resp($d)
{
        benc_resp_raw(benc(array(type => "dictionary", value => $d)));
}

function benc_resp_raw($x)
{
        header("Content-Type: text/plain");
        header("Pragma: no-cache");
        print($x);
}

foreach (array("passkey","info_hash","peer_id","ip","event") as $x)
{
    $GLOBALS[$x] = "" . $_GET[$x];
}

foreach (array("port","downloaded","uploaded","left") as $x)
{
    $GLOBALS[$x] = 0 + $_GET[$x];
}


if (strpos($passkey, "?")) 
{

    $tmp = substr($passkey, strpos($passkey, "?"));
    $passkey = substr($passkey, 0, strpos($passkey, "?"));
    $tmpname = substr($tmp, 1, strpos($tmp, "=")-1);
    $tmpvalue = substr($tmp, strpos($tmp, "=")+1);
    $GLOBALS[$tmpname] = $tmpvalue;
}



foreach (array("passkey","info_hash","peer_id","port","downloaded","uploaded","left") as $x)
{
    if (!isset($x)) err("Missing key: $x");
}


foreach (array("info_hash","peer_id") as $x)
{
    if (strlen($GLOBALS[$x]) != 20) err("Invalid $x (" . strlen($GLOBALS[$x]) . " - " . urlencode($GLOBALS[$x]) . ")");
}


if (strlen($passkey) != 32) err("Invalid passkey (" . strlen($passkey) . " - $passkey)");



//if (empty($ip) || !preg_match('/^(d{1,3}.){3}d{1,3}$/s', $ip))

$ip = getip();

$rsize = 50;
foreach(array("num want", "numwant", "num_want") as $k)
{
        if (isset($_GET[$k]))
        {
                $rsize = 0 + $_GET[$k];
                break;
        }
}

$agent = $_SERVER["HTTP_USER_AGENT"];

/////////////////////Fix Increase ratio using Firefox //////////////////////
$headers = getallheaders();
if (isset($headers["Cookie"]) || isset($headers["Accept-Language"]) || isset($headers["Accept-Charset"]))
err("Anti-Cheater= You cannot use this agent");
///////////////////end of fix//////////////////////

// Deny access made with a browser...
//if (ereg("^Mozilla\\/", $agent) || ereg("^Opera\\/", $agent) || ereg("^Links ", $agent) || ereg("^Lynx\\/", $agent))
//        err("torrent not registered with this tracker");

if (!$port || $port > 0xffff)
        err("invalid port");

if (!isset($event))
        $event = "";

$seeder = ($left == 0) ? "yes" : "no";

//=============   main prog  =================//
// read info from database  

$link=db_connect();
$empire=new mysqlquery();
global $dbtbpre;

/*  private tracker function 
$valid = @mysql_fetch_row(@mysql_query("SELECT COUNT(*) FROM users WHERE passkey=" . sqlesc($passkey)));

if ($valid[0] != 1) err("Invalid passkey! Re-download the .torrent from $BASEURL");

$res = mysql_query("SELECT id, banned, free, silver, seeders + leechers AS numpeers, UNIX_TIMESTAMP(added) AS ts FROM torrents WHERE " . hash_where("info_hash", $info_hash));

$torrent = mysql_fetch_assoc($res);
if (!$torrent)
        err("torrent not registered with this tracker");
*/

$query="select id, seeders + leechers AS numpeers, UNIX_TIMESTAMP(newstime) AS ts from {$dbtbpre}ecms_torrent where checked=1 and info_hash=$info_hash";
$torrent=$empire->fetch1($query);
$torrentid = $torrent["id"];
$numpeers = $torrent["numpeers"];	

// 输出 连接的peer
$limit = "";
if ($numpeers > $rsize)
{
    $limit = "ORDER BY RAND() LIMIT $rsize";
}
$fields = "seeder, peer_id, ip, port, uploaded, downloaded, userid, UNIX_TIMESTAMP(last_action) AS ts";

$query="SELECT $fields FROM peers WHERE torrent = $torrentid AND connectable = 'yes' $limit";
$sql=$empire->query($query);

$resp = "d" . benc_str("interval") . "i" . $announce_interval . "e" . benc_str("peers") . "l";

unset($self);
while($row=$empire->fetch($sql))
{
	$row["peer_id"] = hash_pad($row["peer_id"]);

    if ($row["peer_id"] === $peer_id)
    {
            $userid = $row["userid"];
            $self = $row;
            continue;
    }

    $resp .= "d" .
            benc_str("ip") . benc_str($row["ip"]) .
            benc_str("peer id") . benc_str($row["peer_id"]) .
            benc_str("port") . "i" . $row["port"] . "e" .
            "e";
}

$resp .= "ee";

$selfwhere = "torrent = $torrentid AND " . hash_where("peer_id", $peer_id);

if (!isset($self))
{
        //$res = mysql_query("SELECT $fields FROM peers WHERE $selfwhere");
        //$row = mysql_fetch_assoc($res);
        $query="SELECT $fields FROM peers WHERE $selfwhere";
        $row=$empire->fetch1($query);
        if ($row)
        {
                $userid = $row["userid"];
                $self = $row;
                if(($connectable=checkconnect($row['ip'],$row['port']))=='yes')
                {
                    $cmd_sql="UPDATE peers SET connectable='yes' $selfwhere";
                    $ret=$empire->query1($cmd_sql); 
                }
        }
}

//// Up/down stats ////////////////////////////////////////////////////////////



if (!isset($self))
{

    //$valid = @mysql_fetch_row(@mysql_query("SELECT COUNT(*) FROM peers WHERE torrent=$torrentid AND passkey=" . sqlesc($passkey)));
    $query="SELECT COUNT(*) FROM peers WHERE torrent=$torrentid";
    $valid=$empire->fetch1($query);

    if ($valid[0] >= 1 && $seeder == 'no') err("Connection limit exceeded! You may only leech from one location at a time.");

    if ($valid[0] >= 3 && $seeder == 'yes') err("Connection limit exceeded!");
    
    // 更新用户 下载量
    /*$rz = mysql_query("SELECT id, uploaded, downloaded, class FROM users WHERE passkey=".sqlesc($passkey)." AND enabled = 'yes' ORDER BY last_access DESC LIMIT 1") or err("Tracker error 2");

    if ($MEMBERSONLY && mysql_num_rows($rz) == 0)

    err("Unknown passkey. Please redownload the torrent from $BASEURL.");
            $az = mysql_fetch_assoc($rz);
            $userid = $az["id"];

    //        if ($left > 0 && $az["class"] < UC_VIP)
            if ($az["class"] < UC_VIP && $waitsystem)
            {
                    $gigs = $az["uploaded"] / (1024*1024*1024);
                    $elapsed = floor((gmtime() - $torrent["ts"]) / 3600);
                    $ratio = (($az["downloaded"] > 0) ? ($az["uploaded"] / $az["downloaded"]) : 1);
                    if ($ratio < 0.5 || $gigs < 5) $wait = 24;
                    elseif ($ratio < 0.65 || $gigs < 6.5) $wait = 12;
                    elseif ($ratio < 0.8 || $gigs < 8) $wait = 6;
                    elseif ($ratio < 0.95 || $gigs < 9.5) $wait = 3;
                    else $wait = 0;
                    if ($elapsed < $wait)
                                    err("Not authorized (" . ($wait - $elapsed) . "h) - READ THE FAQ!");
            }
     更新用户 下载量  结束 */ 
}
/*
else
{
            // Get the last uploaded amount from user account for reference and store it in $last_up
    $rst = mysql_query("SELECT class, uploaded FROM users WHERE id = $userid") or err("Tracker error 5");
    $art = mysql_fetch_array($rst);
    $last_up = $art["uploaded"];
    $class = $art["class"];

        $upthis = max(0, $uploaded - $self["uploaded"]);
        $downthis = max(0, $downloaded - $self["downloaded"]);

        if ($upthis > 0 || $downthis > 0)
        // Initial sanity check xMB/s for 1 second
    if($upthis > 2097152)
    {
        //Work out time difference
        $endtime = time();
        $starttime = $self['ts'];
        $diff = ($endtime - $starttime);
        //Normalise to prevent divide by zero.
        $rate = ($upthis / ($diff + 1));
        //Currently 2MB/s. Increase to 5MB/s once finished testing.
        if ($rate > 2097152)
        {
            if ($class < UC_MODERATOR)
            {
                $rate = mksize($rate);
                $client = $agent;
                $userip = getip();

                auto_enter_cheater($userid, $rate, $upthis, $diff, $torrentid, $client, $userip, $last_up);
            }
        }
    }
    $downthis = $torrent['silver'] == 'yes'?$downthis/2:$downthis;
 mysql_query("UPDATE users SET uploaded = uploaded + $upthis". ($torrent['free']=='no'?", downloaded = downloaded + $downthis ":' '). "WHERE id=$userid") or err("Tracker error 3");
                 
}
*/
///////////////////////////////////////////////////////////////////////////////

function portblacklisted($port)
{
        // direct connect
        if ($port >= 411 && $port <= 413) return true;

        // bittorrent
        if ($port >= 6881 && $port <= 6889) return true;

        // kazaa
        if ($port == 1214) return true;

        // gnutella
        if ($port >= 6346 && $port <= 6347) return true;

        // emule
        if ($port == 4662) return true;

        // winmx
        if ($port == 6699) return true;

        return false;
}

$updateset = array();

if ($event == "stopped")
{
        if (isset($self))
        {
                //mysql_query("DELETE FROM peers WHERE $selfwhere");
                $query="DELETE FROM peers WHERE $selfwhere";
                $empire->fetch1($query);
                if (mysql_affected_rows())
                {
                        if ($self["seeder"] == "yes")
                                $updateset[] = "seeders = seeders - 1";
                        else
                                $updateset[] = "leechers = leechers - 1";
                }
        }
}   //////////////代码看到这里
else
{
        if ($event == "completed")
                $updateset[] = "times_completed = times_completed + 1";

        if (isset($self))
        {
               $query="UPDATE peers SET uploaded = $uploaded, downloaded = $downloaded, to_go = $left, last_action = NOW(), seeder = '$seeder'". ($seeder == "yes" && $self["seeder"] != $seeder ? ", finishedat = " . time() : "") . " WHERE $selfwhere";
                $empire->fetch1($query);
                if (mysql_affected_rows() && $self["seeder"] != $seeder)
                {
                        if ($seeder == "yes")
                        {
                                $updateset[] = "seeders = seeders + 1";
                                $updateset[] = "leechers = leechers - 1";
                        }
                        else
                        {
                                $updateset[] = "seeders = seeders - 1";
                                $updateset[] = "leechers = leechers + 1";
                        }
                }
        }
        else
        {
                if (portblacklisted($port))
                        err("Port $port is blacklisted.");
                /*  用户帐号 是否停用        
                if ($az["parked"] == "yes")
                        err("Error, your account is parked!");
                */
                
                /*  bt client checking
                $useragent = substr($peer_id, 1, 2);
                $agentversion = substr($peer_id, 3, 4);
                if(($useragent != "AZ" && $useragent != "UT") || ($useragent == "AZ" && $agentversion < 2504) || ($useragent == "UT" && $agentversion < 1610))
                err("Client is banned. Please use uTorrent 1.6 or Azureus 2.5!");
                */
                $connectable=checkconnect($ip,$port);

                $query = "INSERT INTO peers (connectable, torrent, peer_id, ip, port, uploaded, downloaded, to_go, started, last_action, seeder, userid, agent, uploadoffset, downloadoffset, passkey) VALUES ('$connectable', $torrentid, " . sqlesc($peer_id) . ", " . sqlesc($ip) . ", $port, $uploaded, $downloaded, $left, NOW(), NOW(), '$seeder', $userid, " . sqlesc($agent) . ", $uploaded, $downloaded, " . sqlesc($passkey) . ")";
                $ret=$empire->fetch1($query);
                if ($ret)
                {
                        if ($seeder == "yes")
                                $updateset[] = "seeders = seeders + 1";
                        else
                                $updateset[] = "leechers = leechers + 1";
                }
        }
}

if ($seeder == "yes")
{
        $updateset[] = "last_action = NOW()";
}

if (count($updateset))
        mysql_query("UPDATE torrents SET " . join(",", $updateset) . " WHERE id = $torrentid");

// g-zip start
if ($_SERVER["HTTP_ACCEPT_ENCODING"] == "gzip")

{

header("Content-Encoding: gzip");

echo gzencode(benc_resp_raw($resp), 9, FORCE_GZIP);

}

else  benc_resp_raw($resp);
// g-zip end


?>
