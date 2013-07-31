<?
/*
// +--------------------------------------------------------------------------+
// | Project:    FTS - Free Torrent Source                                    |
// +--------------------------------------------------------------------------+
// | Module: download.php - Download torrent.                                 |
// | Version: 4.8                                                             |
// +--------------------------------------------------------------------------+
// | This file is part of FTS. Fts is based on TBDev,                         |
// | originally by RedBeard of TorrentBits, extensively modified by           |
// | Gartenzwerg.                                                             |
// |                                                                          |
// | FTS is free software; you can redistribute it and/or modify              |
// | it under the terms of the GNU General Public License as published by     |
// | the Free Software Foundation; either version 2 of the License, or        |
// | (at your option) any later version.                                      |
// |                                                                          |
// | FTS is distributed in the hope that it will be useful,                   |
// | but WITHOUT ANY WARRANTY; without even the implied warranty of           |
// | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            |
// | GNU General Public License for more details.                             |
// |                                                                          |
// | You should have received a copy of the GNU General Public License        |
// | along with FTS; if not, write to the Free Software Foundation,           |
// | Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA            |
// +--------------------------------------------------------------------------+
// | FTS IS FREE SOFTWARE, but it still can contain some encoded files.       |
// +--------------------------------------------------------------------------+
// |                                               Do not remove above lines! |
// +--------------------------------------------------------------------------+
*/
require_once("include/bittorrent.php");
require_once "include/benc.php";

dbconn();


if (!preg_match(':^/(\d{1,10})/(.+)\.torrent$:', $_SERVER["PATH_INFO"], $matches))
        httperr();

$id = 0 + $matches[1];
if (!$id)
        httperr();
$re = mysql_query("SELECT external FROM torrents WHERE id = $id") or sqlerr(__FILE__,__LINE__);
$rw = mysql_fetch_assoc($re);
$res = mysql_query("SELECT name FROM torrents WHERE id = $id") or sqlerr(__FILE__, __LINE__);
$row = mysql_fetch_assoc($res);

$fn = "$torrent_dir/$id.torrent";

if (!$row || !is_file($fn) || !is_readable($fn))
        httperr();


mysql_query("UPDATE torrents SET hits = hits + 1 WHERE id = $id");

if (strlen($CURUSER['passkey']) != 32) {

$CURUSER['passkey'] = md5($CURUSER['username'].get_date_time().$CURUSER['passhash']);

mysql_query("UPDATE users SET passkey='$CURUSER[passkey]' WHERE id=$CURUSER[id]");

}



$dict = bdec_file($fn, (1024*1024));

$exte = $rw['external'] !='' ? true : false;
if(!$exte) {
$dict['value']['announce']['value'] = "$BASEURL/announce.php?passkey=$CURUSER[passkey]";

$dict['value']['announce']['string'] = strlen($dict['value']['announce']['value']).":".$dict['value']['announce']['value'];

$dict['value']['announce']['strlen'] = strlen($dict['value']['announce']['string']);
}
#$row['external']


header("Content-Type: application/x-bittorrent");



print(benc($dict));

?>