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
transno = 1200
addr_list = []

starttime = time.time()
print('Generate retrieving addresses...')
for i in range(transno):
    addr_list.append(Bclientproxy.call('getnewaddress'))

preblockheight = Bclientproxy.getblockcount()

print('Send transactions...')
for each in addr_list:
    txid = Aclientproxy.sendtoaddress(each, 0.01 * COIN)

endtime = time.time()
timelength = endtime - starttime
print('It takes', timelength, 'seconds.')

print('last transaction id:', txid)
print('Waiting last transaction confirmation...')
notconfirm = True
while notconfirm:
    txinfo = Aclientproxy.gettransaction(txid)
    if txinfo['confirmations'] == 0:
        time.sleep(0.005)
    else:
        lastblockheight = Aclientproxy.getblockcount()
        break

content = ''
maxtx = 0
print('Finding the block with most transactions...')
for i in range(preblockheight, lastblockheight+1, 1):
    blockhash = Aclientproxy.call('getblockhash', i)
    blockcontent = Aclientproxy.call('getblock', blockhash)
    content = content + 'blockheight:' + str(i) +', tx number:' + str(len(blockcontent['tx'])) + '\n'
    print('blockheight: ', i, '   tx number:', len(blockcontent['tx']))
    if len(blockcontent['tx']) > maxtx:
        maxtx = len(blockcontent['tx'])
print('maxtx:', maxtx)

tpsmeasure = maxtx / 3
print('tpsmax:', tpsmeasure)

f = open(filename, "w")
content = content + 'tpsmax:' + str(tpsmeasure) + '\n'
f.write(content)
f.close()

