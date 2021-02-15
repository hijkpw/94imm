#!/bin/bash

cd /var/www/94imm/crawler

while true
do
    /usr/bin/python3 crawler_mzt.py &
    /usr/bin/python3 crawler_amn.py &
    /usr/bin/python3 crawler_mm131.py &
    /usr/bin/python3 crawler_xmt.py &

    sec=`shuf -i 7200-21600 -n 1`
    date
    echo "sleep $sec s"
    echo ""
    echo ""
    echo ""
    echo ""
    sleep $sec
done
