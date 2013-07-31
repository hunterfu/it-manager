<?
/*
// +--------------------------------------------------------------------------+
// | Project:    FTS - Free Torrent Source                                    |
// +--------------------------------------------------------------------------+
// | Module: scarpe.php - Site's scarpe.                                      |
// | Version: 0.1.2                                                             |
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
require_once("include/benc.php");

dbconn(false);

$r = "d" . benc_str("files") . "d";

$fields = "info_hash, times_completed, seeders, leechers";

if (!isset($_GET["info_hash"]))
        $query = "SELECT $fields FROM torrents ORDER BY info_hash";
else
        $query = "SELECT $fields FROM torrents WHERE " . hash_where("info_hash", unesc($_GET["info_hash"]));

$res = mysql_query($query);

while ($row = mysql_fetch_assoc($res)) {
        $r .= "20:" . hash_pad($row["info_hash"]) . "d" .
                benc_str("complete") . "i" . $row["seeders"] . "e" .
                benc_str("downloaded") . "i" . $row["times_completed"] . "e" .
                benc_str("incomplete") . "i" . $row["leechers"] . "e" .
                "e";
}

$r .= "ee";

// g-zip start
if ($_SERVER["HTTP_ACCEPT_ENCODING"] == "gzip")

{

header("Content-Type: text/plain");

header("Content-Encoding: gzip");

echo gzencode($r, 9, FORCE_GZIP);

}

else {

header("Content-Type: text/plain");

echo $r;

}
// g-zip end

?>