#!/usr/bin/env python3

import time, os

import bitcoin.rpc
from bitcoin.wallet import CBitcoinAddress
from bitcoin.core import b2lx, lx, COIN

pwd = os.getcwd()

clientconf = pwd + '/log/2/bitcoin.conf'
Bclientproxy = bitcoin.rpc.Proxy(btc_conf_file = clientconf)

clientconf = pwd + '/log/1/bitcoin.conf'
Aclientproxy = bitcoin.rpc.Proxy(btc_conf_file = clientconf)

filename = pwd + '/log/tpsdata.txt'
#count = 10
transno = 5000

for i in range(transno):
	newaddress = Aclientproxy.call('getnewaddress')
	txid = Bclientproxy.sendtoaddress(newaddress, 0.01 * COIN)
#	if not (i % 100):
#		print('i:',i)
		
preblockheight = Bclientproxy.getblockcount()

notincrease = True

while notincrease:
	blockheight = Bclientproxy.getblockcount()
	if blockheight > preblockheight:
		break
	else:
		time.sleep(1)


blockhash = Bclientproxy.call('getblockhash', blockheight)

blockcontent = Bclientproxy.call('getblock', blockhash)

#print('blockcontent type:', type(blockcontent))

print('tx number:', len(blockcontent['tx']))

tpsmeasure = len(blockcontent['tx']) / 3

f = open(filename, "w")
content = str(tpsmeasure) + '\n'
f.write(content)
f.close()







