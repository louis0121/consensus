#!/bin/bash

nodecount=5

basepath=$(cd `dirname $0`; pwd)
echo "Stop Bitcoin regtest network."
for ((i=1;i<=$nodecount;i++))
do
	bitcoin-cli -datadir=$basepath/log/$i/ stop
done





