#!/usr/bin/env python3

import socket, threading, time, json, sys, hashlib

import glovar

from consistent import TIME_INTERVAL, IDCONST

import logging

# Message handle function
class msghandle(threading.Thread):
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
		
#		timelog = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()) + 'Start Message thread process'
#		print(timelog)
		self.logger.info('Start Message handle thread process')
		while True:
			message = glovar.msgqueue.get()
			self.connectednode = message[0]
			msgdata = message[1]
			self.addr = message[2]
			data = json.loads(msgdata.decode('utf-8'))
					
			# Receive connected in identity
#			if data['type'] == 'identity':
#				self.__identity_handle(data)
		
			# Receive a public id mined by others
			if data['type'] == 'minedid':
				self.__minedid_handle(data)	
					
			# Receive an idblock mined by others
			elif data['type'] == 'idblock':
				self.__idblock_handle(data)	
			# Unkown received data
			else:
				print('unkown msg!')

	# handle connection information
#	def __identity_handle(self, data):
#		node_identity = (data['address'], data['port'])
#		if node_identity in glovar.CONNECTEDADDR_LIST:
#			self.connectednode.sock.close()
#			glovar.threadLock.acquire()
#			glovar.CONNECTION_LIST.remove(self.connectednode)
#			glovar.CONNECTION_NUMBER -= 1
#			glovar.threadLock.release()
#			#print(node_identity, 'is already in current CONNECTEDADDR_LIST. Disconnect from', self.connectednode.addr)
#			#logcontent = str(node_identity) + 'is already in current CONNECTEDADDR_LIST. Disconnect from' + str(self.connectednode.addr)
#			#self.logger.info(logcontent)
#		else:
#			glovar.threadLock.acquire()
#			glovar.CONNECTEDADDR_LIST.append(node_identity)
#			self.connectednode.addr = node_identity
#			glovar.threadLock.release()
#			logcontent = 'Host:' + str(node_identity) + 'connected in.' + str(glovar.CONNECTION_NUMBER) + ' connections has established.'
#			self.logger.info(logcontent)
#			#print('Current CONNECTEDADDR_LIST is:', glovar.CONNECTEDADDR_LIST)
#			logcontent = 'Current CONNECTEDADDR_LIST is:' + str(glovar.CONNECTEDADDR_LIST)
#			self.logger.info(logcontent)
			
	# Handle mined id information
	def __minedid_handle(self, data):
		if data['hashid'] not in glovar.HASHID_POOL:
			temp = str(data['prevhash']) + data['pubkey'] + str(data['timepoint']) + str(data['nounce'])
			hashvalue = int(hashlib.sha256(temp.encode('utf-8')).hexdigest(), 16)
			if hashvalue < data['target'] and data['target'] == glovar.MINING_TARGET and ( data['timepoint'] - time.time() < TIME_INTERVAL):
				#print('Received valid id:', data['hashid'])
				new_poolidentity = [data['hashid'], data['pubkey'], data['timepoint'], data['nounce'], data['prevhash']]
				glovar.threadLock.acquire()
				glovar.IDENTITY_POOL.append(new_poolidentity)
				glovar.HASHID_POOL.append(data['hashid'])
				glovar.broadqueue.put(data)
				glovar.threadLock.release()
				
	# Handle idblock information
	def __idblock_handle(self, data):
#		timelog = time.strftime('\n%Y-%m-%d %H:%M:%S', time.localtime()) + ' receive an idblock.'
#		print(timelog)
		self.logger.info(' receive an idblock.')
		blockdata = json.loads(data['blockcontent'])
		#print('blockheight:', blockdata[0], '\n timstap: ', blockdata[1], '\n target: ',blockdata[2], '\n prevhash: ', blockdata[3], '\n blockhash: ', blockdata[4], '\n idnumber: ', blockdata[5])
		logcontent = '\nblockheight:' + str(blockdata[0]) + '\ntimstap: ' + str(blockdata[1]) + '\ntarget: ' + str(blockdata[2]) + '\nprevhash: ' + str(blockdata[3]) + '\nblockhash: ' + str(blockdata[4]) + '\nidnumber: ' + str(blockdata[5])
		self.logger.info(logcontent)
		glovar.threadLock.acquire()
		if blockdata[4] not in glovar.block_idpool:
			glovar.blockqueue.put(blockdata)
		glovar.threadLock.release()


