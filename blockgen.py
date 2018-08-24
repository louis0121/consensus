#!/usr/bin/env python3

import sys, time, threading, hashlib, json, logging

import glovar

from consistent import BLOCKGEN_POINT, IDCONST, CHAIN_SHOWTIME

#from network import BroadMsg

# Block generation process
class BlockGeneration(threading.Thread):
	def __init__(self, logdirectory):
		threading.Thread.__init__(self)
		self.unit = BLOCKGEN_POINT
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
		
		self.logger.info('Start ID block generation process')
		try:
#			timelog = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()) + 'Start ID block generation process'
#			print(timelog)
			cur_time = int(time.time())
			prev_time = cur_time - ( cur_time % BLOCKGEN_POINT )
			notstart = True
			while notstart:
				cur_time = int(time.time())
				if cur_time > prev_time + BLOCKGEN_POINT:
#					timelog = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()) + 'ID Block generation start...'
#					print(timelog)
					self.logger.info('ID Block generation start...')
					notstart = False
				else:
					time.sleep(1)
					
			cur_time = int(time.time())
			prev_time = cur_time - ( cur_time % self.unit )
			while True:
				cur_time = int(time.time())
				date_stamp = ( cur_time - ( cur_time % self.unit ) )
				if date_stamp > prev_time:
					generatethread = threading.Thread(target=self.__genidblock)
					generatethread.start()
					prev_time = date_stamp
				else:
					time.sleep(1)
			
		except Exception as e:
			self.logger.info(e)
			
	def __genidblock(self):
#		timelog = time.strftime('\n%Y-%m-%d %H:%M:%S ', time.localtime()) + 'Generate an id block'
#		print(timelog)
		self.logger.info('Generate an id block')
		timestamp = time.time()
		glovar.threadLock.acquire()
		logcontent = '\nglovar.Pool_isbackup:' + str(glovar.Pool_isbackup)
		self.logger.info(logcontent)
		if glovar.Pool_isbackup:
			idgeneration_pool = glovar.BACK_POOL.copy()
			prevblockhash = glovar.BACKPREV_BLOCKHASH
			blockheight = glovar.BACKMINEDBLOCK_HEIGHT
			blocktarget = glovar.BACKMINING_TARGET
			glovar.Generating_height = blockheight + 1
			glovar.Pool_isbackup = False
		else:
			idgeneration_pool = glovar.IDENTITY_POOL.copy()
			prevblockhash = glovar.PREV_BLOCKHASH
			blockheight = glovar.MINEDBLOCK_HEIGHT
			blocktarget = glovar.MINING_TARGET
			glovar.Generating_height = blockheight + 1
		glovar.threadLock.release()

		str_convert = ''
		for each in idgeneration_pool:
			str_convert += ''.join(str(x) for x in each)
		pool_idnumber = len(idgeneration_pool)

		temp = str(prevblockhash) + str_convert + str(timestamp)
		hashvalue = int(hashlib.sha256(temp.encode('utf-8')).hexdigest(), 16)
		newblock = [blockheight, timestamp, blocktarget, prevblockhash, hashvalue, pool_idnumber, idgeneration_pool]
#		print('blockheight:', newblock[0], '\n timstap: ', newblock[1], '\n target: ',newblock[2], '\n prevhash: ', newblock[3], '\n blockhash: ', newblock[4], '\n idnumber: ', newblock[5])
		logcontent = '\nblockheight:' + str(newblock[0]) + '\ntimstap: ' + str(newblock[1]) + '\ntarget: ' + str(newblock[2]) + '\nprevhash: ' + str(newblock[3]) + '\nblockhash: ' + str(newblock[4]) + '\nidnumber: ' + str(newblock[5])
		self.logger.info(logcontent)
		
		glovar.threadLock.acquire()
		glovar.blockqueue.put(newblock)
		glovar.threadLock.release()

# Log the state of IDBLOCKCHAIN
class BlockchainShow(threading.Thread):
	def __init__(self, logdirectory):
		threading.Thread.__init__(self)
		self.logdirectory = logdirectory
		
	def run(self):
		self.logger = logging.getLogger(__name__)
#		timelog = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()) + 'IDBlockchain output to chainlog.txt is started...'
#		print(timelog)
		self.logger.info('IDBlockchain adn IDkeychain log proecess is started')
		
		try:
			filename = self.logdirectory + 'chainstatelog.txt'
			f = open(filename, "w")
			
			IDkeyname = self.logdirectory + 'idkeychain.txt'
			fid = open(IDkeyname, "w")
			
#			timelog = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()) + 'Start IDBLOCKCHAIN logfile process'
#			print(timelog)
			cur_time = int(time.time())
			prev_time = cur_time - ( cur_time % BLOCKGEN_POINT ) + CHAIN_SHOWTIME
			notstart = True
			while notstart:
				cur_time = int(time.time())
				if cur_time > prev_time + BLOCKGEN_POINT:
#					timelog = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()) + 'IDBLOCKCHAIN logfile process start...'
#					print(timelog)
					self.logger.info('Start IDBlockchain adn IDkeychain log proecess...')
					notstart = False
				else:
					time.sleep(1)
					
			prev_time += BLOCKGEN_POINT
			while True:
				date_stamp = int(time.time())
				if date_stamp > prev_time:
					timelog = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()) + 'IDKEYCHAIN:' + '\n'
					
					fid.write(timelog)
					for each in glovar.IDKEYCHAIN:
						count = 0
						for every in each:
							term = str(every[5]) + ' ' + str(every[1]) + '\n'
							fid.write(term)
							count += 1
						term = str(count) + '\n\n'
						fid.write(term)
						
					timelog = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()) + 'IDBLOCKCHAIN:' + '\n'
					f.write(timelog)
					for each in glovar.IDBLOCKCHAIN:
						timelog = ''
						for i in range(6):
							timelog = timelog + str(each[i]) + '\n'
						f.write(timelog)
						timelog = ''
						for i in range(each[5]):
							timelog = timelog + str(each[6][i][1]) + '\n'
						f.write(timelog)
						f.write('\n')
						
					prev_time += BLOCKGEN_POINT
				else:
					time.sleep(2)
			
		except Exception as e:
			self.logger.info(e)
		
		finally:
			f.close()

# function test
if __name__ == '__main__':
	blockgenprocess = BlockGeneration()
	blockgenprocess.start()
