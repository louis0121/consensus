#!/bin/bash

# Read parameters from config file
function __readINI() {
 INIFILE=$1;	SECTION=$2;	ITEM=$3
 _readIni=`awk -F '=' '/\['$SECTION'\]/{a=1}a==1&&$1~/'$ITEM'/{print $2;exit}' $INIFILE`
echo ${_readIni}
}

INFILE=measure.ini
SECTION=runconf

runnode=$(__readINI $INFILE $SECTION runnode)
startport=$(__readINI $INFILE $SECTION startport)

basepath=$(pwd)

for ((i=1;i<=$runnode;i++))
do
	logpath=$basepath/log/$i/
	confpath=$basepath/log/$i/bitcoin.conf
	clientport=`expr $startport + $i`
	touch $logpath/clicf.ini
	port1=`expr $startport + $i - 1`
	#port2=`expr $startport + $i + 1`
	filecontent="[baseconf]\nnodenumber=1\nhost1=localhost\nport1=$port1"
	echo -e $filecontent > ./log/$i/clicf.ini
    ./minernode.py $logpath $confpath $clientport &
#	echo "start client $i"
	sleep 8
done

#netstat -apt | grep python3

