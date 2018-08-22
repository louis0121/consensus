#!/usr/bin/env python3

import os, time, threading, logging, #pdb

import bitcoin.rpc
from bitcoin.wallet import CBitcoinAddress
from bitcoin.core import b2lx, lx, COIN

teststate = [0,0,0]
testover = [0,0,0]

class MeasureProcessing(threading.Thread):
    def __init__(self, sendclient, txnumber):
        threading.Thread.__init__(self)
        self.sendclient = sendclient
        self.txnumber = txnumber

    def run(self):
        global teststate
        global testover
        pwd = os.getcwd()
        clientconf = pwd + '/log/' + str(self.sendclient+3) + '/bitcoin.conf'
        Bclientproxy = bitcoin.rpc.Proxy(btc_conf_file = clientconf)
        clientconf = pwd + '/log/' + str(self.sendclient) + '/bitcoin.conf'
        Aclientproxy = bitcoin.rpc.Proxy(btc_conf_file = clientconf)

        filename = pwd + '/log/tpsdata' + str(self.sendclient) +'.txt'
        self.logger = logging.getLogger(str(self.sendclient))
        self.logger.setLevel(level = logging.INFO)
        handler = logging.FileHandler(filename)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.info('-----------------------------------------------------------')
        self.logger.info('Start tps measurement process!')

        transno = self.txnumber
        addr_list = []
        logcontent = 'client:' + str(self.sendclient+3) + ' generate retrieving addressess...'
        self.logger.info(logcontent)
        #print('client:', self.sendclient+3, ' generate retrieving addresses...')
        starttime = time.time()
        for i in range(transno):
            addr_list.append(Bclientproxy.call('getnewaddress'))

        preblockheight = Bclientproxy.getblockcount()
        
        logcontent = 'client:' + str(self.sendclient) + ' send transactions...'
        self.logger.info(logcontent)
        #print('client:', self.sendclient, ' send transactions...')
        for each in addr_list:
            txid = Aclientproxy.sendtoaddress(each, 0.01 * COIN)
        
        #pdb.set_trace()
        print('COIN:', COIN)

        endtime = time.time()
        timelength = endtime - starttime
        logcontent = 'client:' + str(self.sendclient) + ' takes ' + str(timelength) + ' seconds.'
        self.logger.info(logcontent)
        #print('client:', self.sendclient, 'takes', timelength, 'seconds.')

        logcontent = 'client:' + str(self.sendclient) + ' waiting for last transaction confirmation...'
        self.logger.info(logcontent)
        teststate[self.sendclient-1] = 1
        #print('client:', self.sendclient, ' last transaction id:', txid)
        #print('client:', self.sendclient, ' waiting last transaction confirmation...')
        notconfirm = True
        while notconfirm:
            txinfo = Aclientproxy.gettransaction(txid)
            if txinfo['confirmations'] == 0:
                time.sleep(2)
            else:
                lastblockheight = Aclientproxy.getblockcount()
                break
            
        #content = ''
        maxtx = 0
        logcontent = 'client:' + str(self.sendclient) + ' find the block with most transactions...\n'
        self.logger.info(logcontent)
        #print('client:', self.sendclient, ' find the block with most transactions...')
        for i in range(preblockheight, lastblockheight+1, 1):
            blockhash = Aclientproxy.call('getblockhash', i)
            blockcontent = Aclientproxy.call('getblock', blockhash)
            logcontent = 'blockheight:' + str(i) +', tx number:' + str(len(blockcontent['tx']))
            self.logger.info(logcontent)
            #print('client:', self.sendclient, ' find: blockheight: ', i, '   tx number:', len(blockcontent['tx']))
            if len(blockcontent['tx']) > maxtx:
                maxtx = len(blockcontent['tx'])

        logcontent = 'client:' + str(self.sendclient) + ' find maxtx:' + str(maxtx)
        self.logger.info(logcontent)
        #print('client:', self.sendclient, ' find maxtx:', maxtx)
        
        tpsmeasure = maxtx / 3
        logcontent = 'client:' + str(self.sendclient) + ' find tpsmax:' + str(tpsmeasure)
        self.logger.info(logcontent)
        testover[self.sendclient-1] = 1
        #print('client:', self.sendclient, 'find tpsmax:', tpsmeasure)

        #f = open(filename, "w")
        #content = content + 'tpsmax:' + str(tpsmeasure) + '\n'
        #f.write(content)
        #f.close()

# function test         
if __name__ == '__main__':
    trannum = 3000
    sendnum = 3
    txnumber = trannum // sendnum
    
    for i in range(3):
        meaclient = MeasureProcessing(i+1,txnumber)
        meaclient.start()
    
    notready = True
    while notready:
        if (teststate[0] and teststate[1] and teststate[2]):
            break
        else:
            time.sleep(5)

#    print('start service.')
    os.system("./service.sh")

    while notready:
        if (testover[0] and testover[1] and testover[2]):
            break
        else:
            time.sleep(10)

#    print('end service.')
    os.system("./endservice.sh")

