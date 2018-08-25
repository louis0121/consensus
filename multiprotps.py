#!/usr/bin/env python3

import sys, os, time, threading, logging, configparser#, pdb
import multiprocessing
import queue

import bitcoin.rpc
from bitcoin.wallet import CBitcoinAddress
from bitcoin.core import b2lx, lx, COIN

class MeasureProcessing(multiprocessing.Process):
    def __init__(self, sendclient, txnumber, sendnum, fname, lock):
        multiprocessing.Process.__init__(self)
        self.sendclient = sendclient
        self.txnumber = txnumber
        self.sendnum = sendnum
        self.fname = fname
        self.lock = lock

    def run(self):
        global teststate
        global testover
        pwd = os.getcwd()
        clientconf = pwd + '/log/' + str(self.sendclient+self.sendnum) + '/bitcoin.conf'
        Bclientproxy = bitcoin.rpc.Proxy(btc_conf_file = clientconf)
        clientconf = pwd + '/log/' + str(self.sendclient) + '/bitcoin.conf'
        Aclientproxy = bitcoin.rpc.Proxy(btc_conf_file = clientconf)

        syncname = pwd + '/log/' + self.fname
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
        logcontent = 'client:' + str(self.sendclient+self.sendnum) + ' generate retrieving addressess...'
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
        #print('COIN:', COIN)

        endtime = time.time()
        timelength = endtime - starttime
        logcontent = 'client:' + str(self.sendclient) + ' takes ' + str(timelength) + ' seconds to send transactions.'
        self.logger.info(logcontent)
        #print('client:', self.sendclient, 'takes', timelength, 'seconds.')

        logcontent = 'client:' + str(self.sendclient) + ' waiting for last transaction confirmation...'
        self.logger.info(logcontent)

        self.lock.acquire()
        fs = open(syncname, 'r')
        line = fs.readline()
        #print("line:", line)
        resu = int(line) + 1
        output = str(resu)
        #print("output:", output)
        fs.close()
        fs = open(syncname, 'w')
        fs.write(output)
        fs.close()
        self.lock.release()
        print("Process:", self.sendclient)#, "teststate[", self.sendclient-1, "]:", teststate[self.sendclient-1])
        #print('client:', self.sendclient, ' last transaction id:', txid)
        #print('client:', self.sendclient, ' waiting last transaction confirmation...')
        notconfirm = True
        while notconfirm:
            txinfo = Aclientproxy.gettransaction(txid)
            if txinfo['confirmations'] == 0:
                time.sleep(1)
            else:
                lastblockheight = Aclientproxy.getblockcount()
                break
            
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
            if len(blockcontent['tx']) - 1 > maxtx:
                maxtx = len(blockcontent['tx']) - 1

        logcontent = 'client:' + str(self.sendclient) + ' find maxtx:' + str(maxtx)
        self.logger.info(logcontent)
        #print('client:', self.sendclient, ' find maxtx:', maxtx)
        
        tpsmeasure = maxtx / 3
        logcontent = 'client:' + str(self.sendclient) + ' find tpsmax:' + str(tpsmeasure)
        self.logger.info(logcontent)

        self.lock.acquire()
        fs = open(syncname, 'r')
        line = fs.readline()
        #print("line:", line)
        resu = int(line) + 1
        output = str(resu)
        #print("output:", output)
        fs.close()
        fs = open(syncname, 'w')
        fs.write(output)
        fs.close()
        self.lock.release()
        #print('client:', self.sendclient, 'find tpsmax:', tpsmeasure)

# main function
def main():
    pwd = os.getcwd()
    cf = configparser.ConfigParser()
    cfpath = pwd + '/measure.ini'
    cf.read(cfpath)

    trannum = int(cf.get('measureconf', 'sendtrannum'))
    sendnum = int(cf.get('measureconf', 'sendnodenum'))
    broadtime = int(cf.get('measureconf', 'broadtime'))
    
    txnumber = trannum // sendnum
    
    fname = "notify.txt"
    syncname = pwd + '/log/' + fname
    lock = multiprocessing.Lock()
    lock.acquire()
    fs = open(syncname, 'w')
    fs.write("0")
    fs.close()
    lock.release()

    for i in range(sendnum):
        meaclient = MeasureProcessing(i+1,txnumber,sendnum,fname,lock)
        meaclient.start()
    
    notready = True
    while notready:
        lock.acquire()
        fs = open(syncname, 'r')
        line = fs.readline()
        lock.release()
        if int(line) == sendnum:
            print("start service.")
            break
        else:
            time.sleep(5)


    time.sleep(broadtime)
#    print('start service.')
    os.system("./service.sh")

    while notready:
        lock.acquire()
        fs = open(syncname, 'r')
        line = fs.readline()
        lock.release()
        if int(line) == 2*sendnum:
            break
        else:
            time.sleep(5)
            #print("line:", int(line))

#    print('end service.')
    os.system("./endservice.sh")

# function test         
if __name__ == '__main__':
    main()
