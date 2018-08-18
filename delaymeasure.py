#!/usr/bin/env python3

import time, os

import bitcoin.rpc
from bitcoin.wallet import CBitcoinAddress
from bitcoin.core import b2lx, lx, COIN

pwd = os.getcwd()

#print('pwd:', pwd)
#print('pwd type:', type(pwd))

clientconf = pwd + '/log/2/bitcoin.conf'
Bclientproxy = bitcoin.rpc.Proxy(btc_conf_file = clientconf)

clientconf = pwd + '/log/1/bitcoin.conf'
Aclientproxy = bitcoin.rpc.Proxy(btc_conf_file = clientconf)

filename = pwd + '/log/delaydata.txt'
count = 10
f = open(filename, "w")

for i in range(count):
	newaddress = Bclientproxy.call('getnewaddress')
	txid = Aclientproxy.sendtoaddress(newaddress, 1 * COIN)
	notconfirm = True
	startpoint = time.time()
	while notconfirm:
		txinfo = Aclientproxy.gettransaction(txid)
		if txinfo['confirmations'] == 0:
			time.sleep(0.05)
		else:
			stoppoint = time.time()
			notconfirm = False
		
	txdelay = stoppoint - startpoint
	content = str(txdelay) + '\n'
	f.write(content)

f.close()



#Bclibalance = Bclientproxy.getbalance()/COIN
#Aclibalance = Aclientproxy.getbalance()/COIN
#print('Aclibalance:', Aclibalance)
#print('Bclibalance:', Bclibalance)









#txdelay = stoppoint - startpoint

#txdelaytime = stoppoint - txinfo['time']

#txinfo = Bclientproxy.gettransaction(txid)

#txdelaytimereceived = stoppoint - txinfo['timereceived']

#print('Delay of a transaction calculated by program is :', txdelay, 's.')
#print('Delay of a transaction from wallet is :', txdelaytime, 's.')
#print('Delay of a transaction from local B :', txdelaytimereceived, 's.')

#Bclibalance = Bclientproxy.getbalance()/COIN
#Aclibalance = Aclientproxy.getbalance()/COIN
#print('Aclibalance:', Aclibalance)
#print('Bclibalance:', Bclibalance)


