#!/usr/bin/env python3

import socket, threading, time, json

import glovar

from consistent import TIME_INTERVAL, IDCONST

import logging

# IDblock handle function
class Queuehandle(threading.Thread):
	def __init__(self, logdirectory):
		threading.Thread.__init__(self)
		self.logdirectory = logdirectory

	def run(self):	
		filename = self.logdirectory + 'msghandlelog.txt'
		self.logger = logging.getLogger(__name__)
		self.logger.setLevel(level = logging.INFO)
		handler = logging.FileHandler(filename)
		handler.setLevel(logging.INFO)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		handler.setFormatter(formatter)
		self.logger.addHandler(handler)
		
#		timelog = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()) + 'Start Queuehandle process'
#		print(timelog)
		self.logger.info('Start Queuehandle process')
		while True:
			getidblock = glovar.blockqueue.get()
			#print('\nGet an idblock from the queue. blockheight:', getidblock[0], '\n timstap: ', getidblock[1], '\n target: ',getidblock[2], '\n prevhash: ', getidblock[3], '\n blockhash: ', getidblock[4], '\n idnumber: ', getidblock[5])
			
			if getidblock[0] == len(glovar.IDBLOCKCHAIN):
				#print('\nHandle a competing idblock.')
				if time.time() - getidblock[1] < TIME_INTERVAL: # Received block is not expired
					# Verify the received block
					if getidblock[0] == 1:
						if getidblock[5] > glovar.IDBLOCKCHAIN[-1][5]: # Received block has more identities
							self.__replaceblock(getidblock)
							
						elif getidblock[5] == glovar.IDBLOCKCHAIN[-1][5]: # Received block has the same identities with last block
							if getidblock[4] < glovar.IDBLOCKCHAIN[-1][4]: # Received block has smaller hashvalue
								self.__replaceblock(getidblock)
										
					elif getidblock[3] == glovar.IDBLOCKCHAIN[-2][4]: # Receiving a valid block
						if getidblock[5] > glovar.IDBLOCKCHAIN[-1][5]: # Received block has more identities
							self.__replaceblock(getidblock)
							
						elif getidblock[5] == glovar.IDBLOCKCHAIN[-1][5]: # Received block has the same identities with last block
							if getidblock[4] < glovar.IDBLOCKCHAIN[-1][4]: # Received block has smaller hashvalue
								self.__replaceblock(getidblock)
				else:
					self.logger.info('Received block is expired!')
			
			elif getidblock[0] == len(glovar.IDBLOCKCHAIN) + 1:
				if time.time() - getidblock[1] < TIME_INTERVAL: # Received block is not expired
					# Verify the received block
					if len(glovar.IDBLOCKCHAIN) == 0 and getidblock[3] ==0:
						self.__addidblock(getidblock)
						
					else:
						if getidblock[3] == glovar.IDBLOCKCHAIN[-1][4]: # Receiving a valid block
							self.__addidblock(getidblock)
				else:
					self.logger.info('Received block is expired!')
					
	def __replaceblock(self, getidblock):
		#print('Replace the last IDBlock, due to smaller hashvalue!')
		self.logger.info('Replace the last IDBlock, due to smaller hashvalue!')
		if getidblock[5] > 0:
			newtarget = getidblock[2] * IDCONST // getidblock[5]
		else:
			newtarget = getidblock[2] * IDCONST
		# Maintain key blockchain		
		IDkeyblock = []		
		for each in glovar.IDENTITY_LIST:
			for every in getidblock[6]:
				if each[1] == every[1]:
					IDkeyblock.append(each)
					
		glovar.threadLock.acquire()
		glovar.IDKEYCHAIN.pop(-1)
		glovar.IDKEYCHAIN.append(IDkeyblock)
		glovar.IDBLOCKCHAIN.pop(-1)
		glovar.IDBLOCKCHAIN.append(getidblock)
		glovar.PREV_BLOCKHASH = getidblock[4]
		glovar.prev_datablock = getidblock[4]
		glovar.MINING_TARGET = newtarget
		glovar.block_idpool.append(getidblock[4])
		glovar.threadLock.release()
		self.__broadidblock(getidblock)
		
	def __addidblock(self, getidblock):
		#print('Add a new IDBlock to the chain!')
		self.logger.info('Add a new IDBlock to the chain!')
		if getidblock[5] > 0:
			newtarget = getidblock[2] * IDCONST // getidblock[5]
		else:
			newtarget = getidblock[2] * IDCONST
		# Maintain key blockchain
		IDkeyblock = []
		glovar.threadLock.acquire()
		for each in glovar.IDENTITY_LIST:
			for every in getidblock[6]:
				if each[1] == every[1]:
					IDkeyblock.append(each)
			if each[5] <= getidblock[0] - 2:
				#glovar.threadLock.acquire()
				glovar.IDENTITY_LIST.remove(each)
				#glovar.threadLock.release()
		
		if getidblock[0] > 2: # and len(glovar.IDKEYCHAIN[0]) > 0 and glovar.IDKEYCHAIN[0][0][5] <= getidblock[0] - 2:
			#glovar.threadLock.acquire()
			glovar.IDKEYCHAIN.pop(0)
			#glovar.threadLock.release()
		
		#glovar.threadLock.acquire()
		if getidblock[0] == glovar.Generating_height:
			glovar.BACKPREV_BLOCKHASH = glovar.PREV_BLOCKHASH
			glovar.BACKMINEDBLOCK_HEIGHT = glovar.MINEDBLOCK_HEIGHT
			glovar.BACKMINING_TARGET = glovar.MINING_TARGET
			glovar.BACK_POOL = glovar.IDENTITY_POOL.copy()
			glovar.Pool_isbackup = True
		
		glovar.IDKEYCHAIN.append(IDkeyblock)
		glovar.IDBLOCKCHAIN.append(getidblock)
		glovar.MINEDBLOCK_HEIGHT = getidblock[0] + 1
		glovar.PREV_BLOCKHASH = getidblock[4]
		glovar.prev_datablock = getidblock[4]
		glovar.MINING_TARGET = newtarget
		glovar.block_idpool.append(getidblock[4])
		glovar.threadLock.release()
		self.__broadidblock(getidblock)
		
		
	def __broadidblock(self, blockdata):
		json_block = json.dumps(blockdata)
		senddata = {'No':2, 'type':'idblock', 'prevhash':blockdata[3], 'timestamp':blockdata[1], 'blockcontent':json_block}
		glovar.threadLock.acquire()
		glovar.broadqueue.put(senddata)
		glovar.threadLock.release()


