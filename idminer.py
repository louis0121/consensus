#!/usr/bin/env python3

import os, hashlib, time, threading, random, logging

from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret

from consistent import TIME_INTERVAL, BLOCKGEN_POINT

import glovar

#from network import BroadMsg

# Identity mining process               
class MiningProcessing(threading.Thread):
        def __init__(self, logdirectory):
                threading.Thread.__init__(self)
                self.logdirectory = logdirectory
                
        def run(self):
                filename = self.logdirectory + 'msghandlelog.txt'
                self.logger = logging.getLogger(__name__)
                self.logger.setLevel(level = logging.INFO)
                handler = logging.FileHandler(filename)
                handler.setLevel(logging.INFO)
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                delay = 0.0001    # hash speed latency
                try:
#                       timelog = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()) + 'Start mining process'
#                       print(timelog)
                        self.logger.info('Start mining process')
                        cur_time = int(time.time())
                        prev_time = cur_time - ( cur_time % BLOCKGEN_POINT )
                        notstart = True
                        while notstart:
                                cur_time = int(time.time())
                                if cur_time > prev_time + BLOCKGEN_POINT:
#                                       timelog = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()) + 'Start mining...'
#                                       print(timelog)
                                        self.logger.info('Start mining...')
                                        notstart = False
                                else:
                                        time.sleep(1)
                        
                        glovar.threadLock.acquire()
                        prevhash = glovar.PREV_BLOCKHASH
                        blockheight = glovar.MINEDBLOCK_HEIGHT
                        target = glovar.MINING_TARGET
                        glovar.threadLock.release()
                        while True:
                                # generate privatekey and publickey
                                ranseed = os.urandom(32)
                                h = hashlib.sha256(ranseed).digest()
                                seckey = CBitcoinSecret.from_secret_bytes(h)
                                pubkey=seckey._cec_key.get_pubkey().hex()
                                timepoint = time.time()
                                nounce = 0
                                while True:
                                        # resource control
                                        time.sleep(delay)
                                        print('nouce:', nounce)
                                        temp = str(prevhash) + pubkey + str(timepoint) + str(nounce)
                                        hashvalue = int(hashlib.sha256(temp.encode('utf-8')).hexdigest(), 16)
                                        if hashvalue < target:
                                                break
                                        else:
                                                if time.time() - timepoint > TIME_INTERVAL:
                                                        timepoint = time.time()
                                                        #print('timepoint change to:', timepoint)
                                                        nounce = 0
                                                else:
                                                        nounce += 1
                                                        
                                        glovar.threadLock.acquire()
                                        if prevhash != glovar.PREV_BLOCKHASH: # the state of IDBLOCKCHAIN changed
                                                blockheight = glovar.MINEDBLOCK_HEIGHT
                                                target = glovar.MINING_TARGET
                                                prevhash = glovar.PREV_BLOCKHASH
                                                glovar.IDENTITY_POOL.clear()
                                                glovar.HASHID_POOL.clear()
                                                nounce = 0
                                        glovar.threadLock.release()
                                                
                                new_identity = [seckey, pubkey, timepoint, nounce, target, blockheight]
                                pool_identity = [hashvalue, pubkey, timepoint, nounce, prevhash, target]
                                #print('find hashid: ', hashvalue)
                                
                                glovar.threadLock.acquire()
                                if prevhash == glovar.PREV_BLOCKHASH:  # Having mined an identity before next idblock
                                        glovar.IDENTITY_LIST.append(new_identity)
                                        glovar.IDENTITY_POOL.append(pool_identity)
                                        glovar.HASHID_POOL.append(hashvalue)
                                        glovar.threadLock.release()
                                        # Broadcast new mined identity
                                        senddata = {'No':1, 'hashid':hashvalue, 'pubkey':pubkey, 'prevhash':prevhash, 'timepoint':timepoint, 'nounce':nounce, 'target':target,'type':'minedid'}
                                        glovar.threadLock.acquire()
                                        glovar.broadqueue.put(senddata)
                                        glovar.threadLock.release()
                                else: # the state of IDBLOCKCHAIN changed
                                        blockheight = glovar.MINEDBLOCK_HEIGHT
                                        target = glovar.MINING_TARGET
                                        prevhash = glovar.PREV_BLOCKHASH
                                        glovar.IDENTITY_POOL.clear()
                                        glovar.HASHID_POOL.clear()
                                        glovar.threadLock.release()
                
                except Exception as e:
                        self.logger.info(e)

# function test         
if __name__ == '__main__':
        target = int('000d3fd3f4210c9fb88d8da10a2f86d08d28700c2770a7481ac4fab072f31458', 16)
        user_mining = MiningProcessing()
        user_mining.start()
        
