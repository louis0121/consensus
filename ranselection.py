#!/usr/bin/env python3

import sys, time, threading, hashlib, logging

import glovar

from consistent import DATABLOCK_INTERVAL, BLOCKGEN_POINT, DATABLOCK_FRESH

import bitcoin.rpc
from bitcoin.core import b2lx

# Block generation process
class Datablock(threading.Thread):
        def __init__(self, logdirectory, clientconf):
                threading.Thread.__init__(self)
                self.logdirectory = logdirectory
                self.clientconf = clientconf
                
        def run(self):
                filename = self.logdirectory + 'ranselectionlog.txt'
                self.logger = logging.getLogger(__name__)
                self.logger.setLevel(level = logging.INFO)
                handler = logging.FileHandler(filename)
                handler.setLevel(logging.INFO)
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                
                self.proxy = bitcoin.rpc.Proxy(btc_conf_file = self.clientconf)
                #print('self.clientconf:\n', self.clientconf)
                #self.blockheight = proxy.getblockcount()

                #prevblockhash = b2lx(proxy.getblockhash(self.blockheight))
                #timelog = time.strftime('\n%Y-%m-%d %H:%M:%S ', time.localtime())
                #print(timelog, 'prevblockhash:', prevblockhash)
                
#               timelog = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()) + 'Start random leader selection process...'
#               print(timelog)
                notstart = True
                while notstart:
                        if len(glovar.IDBLOCKCHAIN) >= 2:
#                               timelog = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()) + 'Select the first leader to generate a data block.'
#                               print(timelog)
                                break
                        else:
                                time.sleep(1)

                cur_time = int(time.time())
                prev_time = cur_time - ( cur_time % DATABLOCK_INTERVAL )
                while True:
                        cur_time = int(time.time())
                        self.date_stamp = ( cur_time - ( cur_time % DATABLOCK_INTERVAL ) )
                        if self.date_stamp > prev_time and self.date_stamp % BLOCKGEN_POINT:
                                generatethread = threading.Thread(target=self.__gendatablock)
                                generatethread.start()
                                prev_time = self.date_stamp
                        else:
                                time.sleep(0.5)
                        
        def __gendatablock(self):
                glovar.threadLock.acquire()
                IDblock = glovar.IDBLOCKCHAIN[-2]
                keyblock = glovar.IDKEYCHAIN[0]
                glovar.threadLock.release()
                
                #newproxy = bitcoin.rpc.Proxy(btc_conf_file = self.clientconf)
                self.blockheight = self.proxy.getblockcount()
                prevblockhash = b2lx(self.proxy.getblockhash(self.blockheight))
#               timelog = time.strftime('\n%Y-%m-%d %H:%M:%S ', time.localtime())
#               print(timelog, 'prevblockhash:', prevblockhash)
                temp = prevblockhash + str(IDblock[4]) + str(self.date_stamp)
                if IDblock[5] == 0:
                        return
                pubchosen = int(hashlib.sha256(temp.encode('utf-8')).hexdigest(), 16) % IDblock[5]
                pubkey = IDblock[6][pubchosen][1]
                for each in keyblock:
                        if pubkey == each[1]:
                                #self.proxy.generate(1)
                                r = self.proxy.call('generate', 1)
#                               timelog = time.strftime('%Y-%m-%d %H:%M:%S ', time.localtime()) + 'Generate an bitcoin data block'
#                               print(timelog, '\n', r[0])
                                self.logger.info("----------------------")
                                self.logger.info('Generate an bitcoin data block')
                                self.logger.info(pubchosen)
                                self.logger.info(str(pubkey))
                                self.logger.info("------------------------")
                                
