#!/bin/bash

nodecount=6
iniport=18100
inirpcport=18500

basepath=$(pwd)
echo "Start Bitcoin regtest network."
for ((i=1;i<=$nodecount;i++))
do
	bitcoind -daemon -datadir=$basepath/log/$i/ -conf=$basepath/log/$i/bitcoin.conf
    sleep 2
done

netstat -apt | grep bitcoind

bitcoin-cli -datadir=$basepath/log/1/ getbalance

