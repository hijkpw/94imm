#!/bin/sh
NAME="uwsgi"

function run_start(){
uwsgi --ini uwsgi.ini
}

function run_stop(){
if [ ! -n "$NAME" ];then
    echo "no arguments"
    exit;
fi
ID=`ps -ef | grep "$NAME" | grep -v "$0" | grep -v "grep" | awk '{print $2}'`
for id in $ID
do
kill -9 $id
done
}

function run_clear(){
rm -rf cache/*
}

case "$1" in "start"|"s"|"S")
    run_start
	echo "website run successfully"
	;;
	"restart"|"r"|"S")
	run_stop
	run_clear
	run_start
	echo "website restart successfully"
	;;
	"clear"|"c"|"C")
	run_clear
	echo "cache cleared"
	;;
	"stop")
	run_stop
	echo "website closed"
	;;
	*)
	echo -e "Use command to:\n-s   start website\n-r   restart website\n-c   clear cache\n-stop   stop website"
	;;
	esac
	