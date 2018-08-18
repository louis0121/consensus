#!/bin/bash

nodecount=5
basepath=$(cd `dirname $0`; pwd)

for ((i=1;i<=$nodecount;i++))
do
	logpath=$basepath/log/$i/
	cd $logpath
	rm chainstatelog.txt idkeychain.txt msghandlelog.txt ranselectionlog.txt
	#sleep 0.5
done




