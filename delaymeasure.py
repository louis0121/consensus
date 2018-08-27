#!/usr/bin/env python3

import time, os
import numpy as np
import matplotlib.pyplot as plt

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
count = 5
f = open(filename, "w")

datamatri = []

for i in range(count):
        newaddress = Bclientproxy.call('getnewaddress')
        txid = Aclientproxy.sendtoaddress(newaddress, 1 * COIN)
        notconfirm = True
        startpoint = time.time()
        while notconfirm:
                txinfo = Aclientproxy.gettransaction(txid)
                if txinfo['confirmations'] == 0:
                        time.sleep(0.005)
                else:
                        stoppoint = time.time()
                        break
                
        txdelay = stoppoint - startpoint
        datamatri.append(txdelay)
        content = str(txdelay) + '\n'
        f.write(content)

f.close()

plt.hist(datamatri)
plt.ylabel('Confirmation latency')
plt.savefig("./log/latency.png", dpi=600)
plt.show()


#Aclibalance = Aclientproxy.getbalance()/COIN
#print('Aclibalance:', Aclibalance)

