#!/bin/bash

nodecount=3
startport=18000

basepath=$(cd `dirname $0`; pwd)

#echo $basepath

for ((i=1;i<=$nodecount;i++))
do
	logpath=$basepath/log/$i/
	confpath=$basepath/log/$i/bitcoin.conf
	clientport=`expr $startport + $i`
#	echo $logpath
#	echo $confpath
#	echo $clientport
	#sh worker.sh $logpath $confpath &
	touch $logpath/clicf.ini
	port1=`expr $startport + $i - 1`
	#port2=`expr $startport + $i + 1`
	filecontent="[baseconf]\nnodenumber=1\nhost1=localhost\nport1=$port1"
	echo -e $filecontent > ./log/$i/clicf.ini
    #sudo cpulimit -l 40 
    ./minernode.py $logpath $confpath $clientport &
#	echo "start client $i"
	sleep 8
done

#netstat -apt | grep python3


