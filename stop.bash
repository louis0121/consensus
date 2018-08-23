#!/bin/bash

# Read parameters from config file
function __readINI() {
 INIFILE=$1;	SECTION=$2;	ITEM=$3
 _readIni=`awk -F '=' '/\['$SECTION'\]/{a=1}a==1&&$1~/'$ITEM'/{print $2;exit}' $INIFILE`
echo ${_readIni}
}

INFILE=measure.ini
SECTION=measureconf

nodecount=$(__readINI $INFILE $SECTION bitcoindnum)

basepath=$(pwd)
echo "Stop Bitcoin regtest network."
for ((i=1;i<=$nodecount;i++))
do
	bitcoin-cli -datadir=$basepath/log/$i/ stop
done

