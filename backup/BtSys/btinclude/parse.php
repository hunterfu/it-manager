<?php
//
//  TorrentTrader v2.x
//	This file was last updated: 27/June/2007
//	
//	http://www.torrenttrader.org
//
//

/*array info for ref:
announce
infohash
creation date
intenal name
torrentsize
filecount
announceruls
comment
filelist
*/

require_once("BDecode.php") ;
require_once("BEncode.php") ;

function escape_url($url) {
        $ret = '';
        for($i = 0; $i < strlen($url); $i+=2)
        $ret .= '%'.$url[$i].$url[$i + 1];
        return $ret;
}

function torrent_scrape_url($scrape, $hash) {
        ini_set('default_socket_timeout',10);
        @$fp = file_get_contents($scrape.'?info_hash='.escape_url($hash));
        $ret = array();
        if(!$fp) {
                $ret['seeds'] = -1;
                $ret['peers'] = -1;
        }else{
                $stats = BDecode($fp);
                $binhash = addslashes(pack("H*", $hash));
                $seeds = $stats['files'][$binhash]['complete'];
                $peers = $stats['files'][$binhash]['incomplete'];
                $downloaded = $stats['files'][$binhash]['downloaded'];
                $ret['seeds'] = $seeds;
                $ret['peers'] = $peers;
                $ret['downloaded'] = $downloaded;
        }
        return $ret;
}

function ParseTorrent($filename) {

	$TorrentInfo = array();

	global $array;

	//check file type is a torrent
	$torrent = explode(".", $filename);
    $fileend = end($torrent);
    $fileend = strtolower($fileend);

	if ( $fileend == "torrent" ) {
		$parseme = @file_get_contents("$filename");

	if ($parseme == FALSE) {
		$TorrentInfo[9]="Parser Error: Error Opening torrent, unabled to get contents";
	}

	if(!isset($parseme)){
		$TorrentInfo[9]="Parser Error: Error Opening torrent";
	}else{
		$array = BDecode($parseme);
		if ($array === FALSE){
			$TorrentInfo[9]="Parser Error: Error Opening torrent, unable to decode";
		}else{
			if(array_key_exists("info", $array) === FALSE){
				$TorrentInfo[9]="Error Opening torrent";
			}else{
				//Get Announce URL
				$TorrentInfo[0] = $array["announce"];

				//Get Announce List Array
				if (isset($array["announce-list"])){
					$TorrentInfo[6] = $array["announce-list"];
				}

				//Read info, store as (infovariable)
				$infovariable = $array["info"];
				
				// Calculates SHA1 Hash
				$infohash = sha1(BEncode($infovariable));
				$TorrentInfo[1] = $infohash ;
				
				// Calculates date from UNIX Epoch
				$makedate = date('r' , $array["creation date"]);
				$TorrentInfo[2] = $makedate ;

				// The name of the torrent is different to the file name
				$TorrentInfo[3] = $infovariable['name'] ;

				//Get File List
				if (isset($infovariable["files"]))  {
					// Multi File Torrent
					$filecount = "";

					//Get filenames here
					$TorrentInfo[8] = $infovariable["files"];

					foreach ($infovariable["files"] as $file) {
						$filecount += "1";
						$multiname = $file['path'];//Not needed here really
						$multitorrentsize = $file['length'];
						$torrentsize += $file['length'];
					}

					$TorrentInfo[4] = $torrentsize;  //Add all parts sizes to get total
					$TorrentInfo[5] = $filecount;  //Get file count
				}else {
					// Single File Torrent
					$torrentsize = $infovariable['length'];
					$TorrentInfo[4] = $torrentsize;//Get file count
					$TorrentInfo[5] = "1";
				}

				// Get Torrent Comment
				if(isset($array['comment'])) {
					 $TorrentInfo[7] = $array['comment'];
				}
			}
		}
	}
}
return $TorrentInfo;
}//End Function
?>
