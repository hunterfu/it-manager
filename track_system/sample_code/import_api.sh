#!/usr/bin/env bash
usage() {
    cat <<EOF
Post phy install infomation.
Usage:
    $0 list (host ip sn)
EOF
    exit 1
}
sysinstall=127.0.0.1:8000
test -f "$1" || usage
while read host ip sn
do
        stat=$(curl -X POST -d "hostname=${host}&&ip=${ip}&&sn=${sn}" http://$sysinstall/api/host/ 2>/dev/null)
        echo "$host:$ip:$stat"
done < "$1"
