#!/bin/bash

basepath=$(pwd)
echo "start measure tps of transactions..."

testnum=3
for ((i=1;i<=$testnum;i++))
do
    ./initial.sh

    sleep 2

	./multiprotps.py
    #bitcoin-cli -datadir=$basepath/log/4/ generate 6
    sleep 1
    ./stop.bash
    sleep 2
done

echo "finish measurement."

tpsname="$basepath/tpsrecord.txt"
./plotfig.py $tpsname 

