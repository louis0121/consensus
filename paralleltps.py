#!/usr/bin/env python3

import os, time, threading

import bitcoin.rpc
from bitcoin.wallet import CBitcoinAddress
from bitcoin.core import b2lx, lx, COIN

class MeasureProcessing(threading.Thread):
    def __init__(self, sendclient, txnumber):
        threading.Thread.__init__(self)
        self.sendclient = sendclient
        self.txnumber = txnumber

    def run(self):
        pwd = os.getcwd()
        clientconf = pwd + '/log/' + str(self.sendclient+3) + '/bitcoin.conf'
        Bclientproxy = bitcoin.rpc.Proxy(btc_conf_file = clientconf)
        clientconf = pwd + '/log/' + str(self.sendclient) + '/bitcoin.conf'
        Aclientproxy = bitcoin.rpc.Proxy(btc_conf_file = clientconf)

        filename = pwd + '/log/tpsdata' + str(self.sendclient) +'.txt'
        transno = self.txnumber
        addr_list = []

        print('client:', self.sendclient+3, ' generate retrieving addresses...')
        starttime = time.time()
        for i in range(transno):
            addr_list.append(Bclientproxy.call('getnewaddress'))

        preblockheight = Bclientproxy.getblockcount()
        
        print('client:', self.sendclient, ' send transactions...')
        for each in addr_list:
            txid = Aclientproxy.sendtoaddress(each, 0.01 * COIN)
        
        endtime = time.time()
        timelength = endtime - starttime
        print('client:', self.sendclient, 'takes', timelength, 'seconds.')

        print('client:', self.sendclient, ' last transaction id:', txid)
        print('client:', self.sendclient, ' waiting last transaction confirmation...')
        notconfirm = True
        while notconfirm:
            txinfo = Aclientproxy.gettransaction(txid)
            if txinfo['confirmations'] == 0:
                time.sleep(2)
            else:
                lastblockheight = Aclientproxy.getblockcount()
                break
            
        content = ''
        maxtx = 0
        print('client:', self.sendclient, ' find the block with most transactions...')
        for i in range(preblockheight, lastblockheight+1, 1):
            blockhash = Aclientproxy.call('getblockhash', i)
            blockcontent = Aclientproxy.call('getblock', blockhash)
            content = content + 'blockheight:' + str(i) +', tx number:' + str(len(blockcontent['tx'])) + '\n'
            print('client:', self.sendclient, 'find: blockheight: ', i, '   tx number:', len(blockcontent['tx']))
            if len(blockcontent['tx']) > maxtx:
                maxtx = len(blockcontent['tx'])

        print('client:', self.sendclient, 'find maxtx:', maxtx)
        
        tpsmeasure = maxtx / 3
        print('client:', self.sendclient, 'find tpsmax:', tpsmeasure)

        f = open(filename, "w")
        content = content + 'tpsmax:' + str(tpsmeasure) + '\n'
        f.write(content)
        f.close()

# function test         
if __name__ == '__main__':
    trannum = 7200
    sendnum = 3
    txnumber = trannum // sendnum
    
    for i in range(3):
        meaclient = MeasureProcessing(i+1,txnumber)
        meaclient.start()

