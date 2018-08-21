#!/bin/bash

startport=18000
basepath=$(pwd)
i=1
logpath=$basepath/log/$i/
confpath=$basepath/log/$i/bitcoin.conf
clientport=`expr $startport + $i`
echo $logpath
echo $confpath
echo $clientport
./minernode.py $logpath $confpath $clientport &
echo "start client $i"
sleep 8

netstat -apt | grep python3


