#!/usr/bin/env python3

# Copyright (C) 2018 Mining node
#
# This file is the main program of mining node.

# Check python version to make sure it executes under python3
import sys, os
if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this example.\n')
    sys.exit(1)

# Import required packages
import glovar, configparser
from idminer import *
from msghandle import *
from network import *
from blockgen import *
from queuehandle import *
from ranselection import *

# main function
def main():
        if len(sys.argv) < 4:
                print('Lack of two parameters: logdirectory or clientconf or bindport!')
                pwd = os.getcwd()
                logdirectory = pwd + '/log/1/'
                clientconf = pwd + '/log/1/bitcoin.conf'
                bindport = 18000
                print('Use the default logdirectory, clientconf and bindport.\n',logdirectory,'\n',clientconf,'\n',bindport)
#               sys.exit()
        else:
                logdirectory = sys.argv[1]
                clientconf = sys.argv[2]
                bindport = int(sys.argv[3])
        
        cf = configparser.ConfigParser()
        cfpath = logdirectory + 'clicf.ini'
        cf.read(cfpath)
        nodenumber = int(cf.get('baseconf', 'nodenumber'))
#        print('nodenumber:', nodenumber)
        for i in range(nodenumber):
                host = 'host' + str(i+1)
                port = 'port' + str(i+1)
                hostip = cf.get('baseconf', host)
                hostport = cf.get('baseconf', port)
                #print("host:", hostip)
                #print("port:", hostport)
                glovar.threadLock.acquire()
                glovar.confnode.append((hostip, int(hostport)))
                glovar.threadLock.release()
        
        tcp_server = TcpServer(SERVER_ADDR, bindport, CONNECTIONMAX, logdirectory)
        tcp_server.start()
        msg_handle = msghandle(logdirectory)
        msg_handle.start()
        msg_broad = BroadMsg(logdirectory)
        msg_broad.start()
        
        time.sleep(5)
        tcp_connect = ConnectionCreation(logdirectory)
        tcp_connect.start()
        
        time.sleep(10)
        user_mining = MiningProcessing(logdirectory)
        user_mining.start()
        
        blockgenprocess = BlockGeneration(logdirectory)
        blockgenprocess.start()
        
        outputlog = BlockchainShow(logdirectory)
        outputlog.start()
        
        chain_handle = Queuehandle(logdirectory)
        chain_handle.start()
        
        datablock_gen = Datablock(logdirectory, clientconf)
        datablock_gen.start()

# Execute as main program
if __name__ == '__main__':
        main()

