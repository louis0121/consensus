#!/usr/bin/env python3

import socket, threading, time, json, sys, logging, struct

import glovar

from consistent import SERVER_ADDR, SERVER_PORT, CONNECTIONMAX, RECV_BUFFER, PACKETVER, HEADER_SIZE

from msghandle import msghandle

#Connection node class
class ConnectedNode(threading.Thread):
	def __init__(self, sock, addr, logdirectory):
		threading.Thread.__init__(self)
		self.sock = sock
		self.addr = addr
		self.logdirectory = logdirectory
		
	def senddata(self, data):
		json_data = json.dumps(data)
		header = [PACKETVER, json_data.__len__()]
		headerPack = struct.pack('!2I', *header)
		packdata = headerPack + json_data.encode('utf-8')
		self.sock.send(packdata)

	def run(self):
#		filename = self.logdirectory + 'msghandlelog.txt'
		self.logger = logging.getLogger(__name__)
#		self.logger.setLevel(level = logging.INFO)
#		handler = logging.FileHandler(filename)
#		handler.setLevel(logging.INFO)
#		formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
#		handler.setFormatter(formatter)
#		self.logger.addHandler(handler)
		try:
			dataBuffer = bytes()
			while True:
				data = self.sock.recv(RECV_BUFFER)
				if data:
					dataBuffer += data
					while True:
						if len(dataBuffer) < HEADER_SIZE: #数据包小于消息头部长度，跳出小循环
							break
						
						headPack = struct.unpack('!2I', dataBuffer[:HEADER_SIZE])
						bodySize = headPack[1]
						# 分包情况处理，跳出函数继续接收数据
						if len(dataBuffer) < HEADER_SIZE + bodySize: #数据包不完整，跳出小循环
							break
						# 读取消息正文的内容
						recvdata = dataBuffer[HEADER_SIZE : HEADER_SIZE + bodySize]
						# 数据处理
						queue_data = [self, recvdata, self.addr]
						glovar.threadLock.acquire()
						glovar.msgqueue.put(queue_data)
						glovar.threadLock.release()
						# 粘包情况的处理
						dataBuffer = dataBuffer[HEADER_SIZE + bodySize:] # 获取下一个数据包，类似于把数据pop出
				
		except Exception as e:
			self.logger.info(e)
			
		finally:
			#print("remove self.addr:", self.addr)
			logcontent = 'remove self.addr:' + str(self.addr)
			self.logger.info(logcontent)
			glovar.threadLock.acquire()
			glovar.CONNECTEDADDR_LIST.remove(self.addr)
			glovar.CONNECTION_LIST.remove(self)
			glovar.CONNECTION_NUMBER -= 1
			glovar.threadLock.release()
#			timelog = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' '
#			print(timelog, 'Host:', self.addr, 'disconnected from localhost.', glovar.CONNECTION_NUMBER, "hosts terminal is still connected.")
			logcontent = 'Host:' + str(self.addr) + 'disconnected from localhost.' + str(glovar.CONNECTION_NUMBER) + 'hosts terminal is still connected.'
			self.logger.info(logcontent)
			self.sock.close()
			
# Server Node
class TcpServer(threading.Thread):
	def __init__(self, tcpaddr, tcpport, maxnumber, logdirectory):
		threading.Thread.__init__(self)
		self.tcpaddr = tcpaddr
		self.tcpport = tcpport
		self.maxnumber = maxnumber
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
		
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		# If the default tcp port is already in use, port puls 1 until one tcp port has been binded
#		notbinded = True
#		while notbinded:
		try:
			server_socket.bind((self.tcpaddr, self.tcpport))
			glovar.BINDED_ADDR = glovar.BINDED_ADDR + (self.tcpaddr, self.tcpport)
			#print('glovar.BINDED_ADDR:', glovar.BINDED_ADDR)
			logcontent = 'Bind local port:' + str(glovar.BINDED_ADDR)
			self.logger.info(logcontent)
#			notbinded = False
		except OSError as err:
			#print('OSError:', format(err))
			#print('Port:', self.tcpport, 'is already in use!')
			logcontent = 'Port:' + str(self.tcpport) + 'is already in use!'
			self.logger.info(logcontent)
			raise
#			self.tcpport += 1
				
		server_socket.listen(self.maxnumber)
#		timelog = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' '
#		print(timelog, 'Node is started. Port:', self.tcpport, 'is waiting for connection...')
		logcontent = 'Node is started. Port:' + str(self.tcpport) + ' is waiting for connection...'
		self.logger.info(logcontent)

		while True:
			if glovar.CONNECTION_NUMBER == self.maxnumber:
				time.sleep(5)
			else:
				#print('CONNECTION_NUMBER:', CONNECTION_NUMBER)
				sockfd, addr = server_socket.accept()
				socket_accept_thread = threading.Thread(target=self.__socket_accept, args=(sockfd, addr))
				socket_accept_thread.start()
		server_socket.close()  # Close server

	#Connection acceptance process
	def __socket_accept(self, sockfd, addr):
		user = ConnectedNode(sockfd, addr, self.logdirectory)
		glovar.threadLock.acquire()
		glovar.CONNECTION_LIST.append(user)
		glovar.CONNECTEDADDR_LIST.append(addr)
		glovar.CONNECTION_NUMBER += 1
		glovar.threadLock.release()
#		timelog = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' '
#		print(timelog, 'Host: %s connected in. %d connections has established.' % (addr, glovar.CONNECTION_NUMBER))		
		logcontent = 'Host:' + str(addr) + 'connected in.' + str(glovar.CONNECTION_NUMBER) + ' connections has established.'
		self.logger.info(logcontent)
		user.start()
	
# Connect to node in the NODE_LIST		
class ConnectionCreation(threading.Thread):
	def __init__(self, logdirectory):
		threading.Thread.__init__(self)
		self.logdirectory = logdirectory
		
	def run(self):
#		filename = self.logdirectory + 'msghandlelog.txt'
		self.logger = logging.getLogger(__name__)
#		self.logger.setLevel(level = logging.INFO)
#		handler = logging.FileHandler(filename)
#		handler.setLevel(logging.INFO)
#		formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
#		handler.setFormatter(formatter)
#		self.logger.addHandler(handler)
		glovar.threadLock.acquire()
		NODE_LIST = glovar.confnode
		glovar.threadLock.release()
		
		while True:
			for each in NODE_LIST:
#				glovar.threadLock.acquire()
#				conaddrlist = glovar.CONNECTEDADDR_LIST
#				glovar.threadLock.release()
				if each not in glovar.CONNECTEDADDR_LIST:
#					if each != glovar.BINDED_ADDR:
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
					try:
						sock.connect(each)
#							senddata = {'No':1, 'address':glovar.BINDED_ADDR[0], 'port':glovar.BINDED_ADDR[1], 'type':'identity'}
#							json_data = json.dumps(senddata)
#							header = [PACKETVER, json_data.__len__()]
#							headerPack = struct.pack('!2I', *header)
#							packdata = headerPack + json_data.encode('utf-8')
#							sock.send(packdata)
						user = ConnectedNode(sock, each, self.logdirectory)
					
						glovar.threadLock.acquire()
#							if each not in glovar.CONNECTEDADDR_LIST:
						glovar.CONNECTEDADDR_LIST.append(each)
						glovar.CONNECTION_LIST.append(user)
						glovar.CONNECTION_NUMBER += 1
						glovar.threadLock.release()
						user.start()
#							timelog = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' '
#							print(timelog, 'Success to connect to host: %s. %d connections has established.' % (each, glovar.CONNECTION_NUMBER))
#							print('Current CONNECTEDADDR_LIST is:', glovar.CONNECTEDADDR_LIST)
						logcontent = 'Success to connect to host:' + str(each) + '.' +  str(glovar.CONNECTION_NUMBER) + ' connections has established.'
						self.logger.info(logcontent)
						logcontent = 'Current CONNECTEDADDR_LIST is:' + str(glovar.CONNECTEDADDR_LIST)
						self.logger.info(logcontent)
					
					
							
					except ConnectionRefusedError:
						time.sleep(0.5)
			
			time.sleep(5)

# Broadcast message class
class BroadMsg(threading.Thread):
	def __init__(self, logdirectory):
		threading.Thread.__init__(self)
		self.logdirectory = logdirectory
				
	def run(self):
#		filename = self.logdirectory + 'msghandlelog.txt'
		self.logger = logging.getLogger(__name__)
#		self.logger.setLevel(level = logging.INFO)
#		handler = logging.FileHandler(filename)
#		handler.setLevel(logging.INFO)
#		formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
#		handler.setFormatter(formatter)
#		self.logger.addHandler(handler)
		
#		timelog = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()) + 'Start broadcast message thread process'
#		print(timelog)
		self.logger.info('Start broadcast message thread process')
		while True:
			try:
				sendmsg = glovar.broadqueue.get()
				for each in  glovar.CONNECTION_LIST:
					each.senddata(sendmsg)
			except Exception as e:
				self.logger.info("----------------------")
				self.logger.info(e)
				self.logger.info(sendmsg)
				self.logger.info("------------------------")
				#print(e)

# function test		
if __name__ == '__main__':	
	tcp_server = TcpServer(SERVER_ADDR, SERVER_PORT, CONNECTIONMAX)
	tcp_server.start()
	time.sleep(2)
	tcp_connect = ConnectionCreation()
	tcp_connect.start()

