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
basepath=$(pwd)

for ((i=1;i<=$runnode;i++))
do
	logpath=$basepath/log/$i/
	cd $logpath
	rm chainstatelog.txt idkeychain.txt msghandlelog.txt ranselectionlog.txt
	#sleep 0.5
done




