#!/bin/bash

nodecount=6
iniport=18100
inirpcport=18500

if [ -d ./log ]; then
	echo "./log already exit, remove it."
    rm -r ./log
fi
echo "create new node log directory"
mkdir ./log

for ((i=1;i<=$nodecount;i++))
do
	mkdir ./log/$i
	touch ./log/$i/bitcoin.conf
	port=`expr $iniport + $i`
	rpcport=`expr $inirpcport + $i`
	conport1=`expr $iniport + $i - 1`
    conport2=`expr $iniport + $i - 2`
    conport3=`expr $iniport + $i - 3`
    filecontent="rpcuser = user\nrpcpassword = 123\nregtest = 1\nserver =
    1\nport = $port\nrpcport = $rpcport\naddnode = localhost:$conport1\naddnode
    = localhost:$conport2\naddnode = localhost:$conport3"
	echo -e $filecontent > ./log/$i/bitcoin.conf
done

basepath=$(cd `dirname $0`; pwd)
echo "Start Bitcoin regtest network."
for ((i=1;i<=$nodecount;i++))
do
	bitcoind -daemon -datadir=$basepath/log/$i/ -conf=$basepath/log/$i/bitcoin.conf
    sleep 2
done

#sleep 10

bitcoin-cli -datadir=$basepath/log/1/ generate 30
bitcoin-cli -datadir=$basepath/log/2/ generate 30
bitcoin-cli -datadir=$basepath/log/3/ generate 30
bitcoin-cli -datadir=$basepath/log/4/ generate 100

#sleep 60

netstat -apt | grep bitcoind

bitcoin-cli -datadir=$basepath/log/1/ getbalance
bitcoin-cli -datadir=$basepath/log/2/ getbalance
bitcoin-cli -datadir=$basepath/log/3/ getbalance


