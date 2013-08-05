#!/bin/sh
set -e
base_dir=`dirname $0`
torrent_dir="$base_dir/torrent"
TORRENT_FILE=$1
dumptorrent="$base_dir/dumptorrent"
tmp_file="/tmp/dum_ptorrent"
$dumptorrent -v $TORRENT_FILE > $tmp_file
info_hash=`cat $tmp_file | grep 'Info Hash' | awk -F : '{print $2}' | sed -r 's/^\s+//'`
creation_date=`cat $tmp_file | grep 'Creation Date' | sed -r 's/Creation Date:\s+//'`

# 根据torrent的创建时间来建立保存torrent目录
dir_date=`date -d "$creation_date" +%Y-%m`;
save_dir="$torrent_dir/$dir_date";
if [ ! -d $save_dir ];then
    mkdir -p $save_dir
fi

dest_file="$save_dir/$info_hash.torrent"

if [ ! -e $dest_file ];then 
    cp $TORRENT_FILE $save_dir/"$info_hash.torrent"
fi
