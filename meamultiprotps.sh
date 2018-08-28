#!/bin/bash

./initial.sh

sleep 2

basepath=$(pwd)
echo "start measure tps of transactions..."

testnum=3
for ((i=1;i<=$testnum;i++))
do
	./multiprotps.py
    bitcoin-cli -datadir=$basepath/log/4/ generate 6
    sleep 1
done

echo "finish measurement."

tpsname="$basepath/log/tpsrecord.txt"
./plotfig.py $tpsname 

./stop.bash
