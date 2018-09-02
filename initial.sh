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
iniblock=$(__readINI $INFILE $SECTION iniblocknum)
bitcoindconnum=$(__readINI $INFILE $SECTION bitcoindconnum)
sendnodenum=$(__readINI $INFILE $SECTION sendnodenum)

if [ -d ./log ]; then
	echo "./log already exit, remove it."
    rm -r ./log
fi
echo "create new node log directory"
mkdir ./log

basepath=$(pwd)
for ((i=1;i<=$nodecount;i++))
do
	mkdir ./log/$i
	touch ./log/$i/bitcoin.conf
	port=`expr $iniport + $i`
	rpcport=`expr $inirpcport + $i`

    preaddnode="\naddnode = localhost:"
    addnode=""
    for ((j=1;j<=$bitcoindconnum;j++))
    do
        conport=`expr $iniport + $i - $j`
        midaddnode=${preaddnode}${conport}
        addnode=${addnode}${midaddnode}
    done

    filecontent="rpcuser = user\nrpcpassword = 123\nregtest = 1\nserver =
    1\nport = $port\nrpcport = $rpcport"$addnode

	echo -e $filecontent > ./log/$i/bitcoin.conf

	bitcoind -daemon -datadir=$basepath/log/$i/ -conf=$basepath/log/$i/bitcoin.conf >> mealog.txt
    sleep 5
done

echo "Initial block generation..."

for ((i=1;i<=$sendnodenum;i++))
do
    bitcoin-cli -datadir=$basepath/log/$i/ generate $iniblock >> mealog.txt
    sleep 3
done

lastnode=`expr $sendnodenum + 1`
bitcoin-cli -datadir=$basepath/log/$lastnode/ generate 100 >> mealog.txt

#netstat -apt | grep bitcoind
sleep 2

for ((i=1;i<=$sendnodenum;i++))
do
    bitcoin-cli -datadir=$basepath/log/$i/ getbalance
done

