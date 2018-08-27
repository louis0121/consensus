#!/bin/bash

./initial.sh

sleep 2

echo "start measure tps of transactions..."

testnum=10
for ((i=1;i<=$testnum;i++))
do
	./multiprotps.py
done

echo "finish measurement."

basepath=$(pwd)
tpsname="$basepath/log/tpsrecord.txt"
./plotfig.py $tpsname 

./stop.bash
