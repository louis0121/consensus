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
iniport=$(__readINI $INFILE $SECTION bitcoindiniport)
inirpcport=$(__readINI $INFILE $SECTION bitcoindinirpcport)

basepath=$(pwd)
echo "Start Bitcoin regtest network."
for ((i=1;i<=$nodecount;i++))
do
	bitcoind -daemon -datadir=$basepath/log/$i/ -conf=$basepath/log/$i/bitcoin.conf
    sleep 2
done

netstat -apt | grep bitcoind

bitcoin-cli -datadir=$basepath/log/1/ getbalance

