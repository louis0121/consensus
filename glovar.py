#!/usr/bin/env python3
import threading, queue

threadLock = threading.Lock()

blockqueue = queue.Queue()
msgqueue = queue.Queue()
broadqueue = queue.Queue()
# Netowrk config
CONNECTION_LIST = []	# Node connection list
CONNECTEDADDR_LIST = [] 
CONNECTION_NUMBER = 0
BINDED_ADDR = ()
confnode = []

# Mining config
IDENTITY_LIST = []
IDKEYCHAIN = []
IDENTITY_POOL = []
HASHID_POOL = []
IDPREPARECHAIN = []

# State of blockchain and mining parameters
IDBLOCKCHAIN = []
MINING_TARGET = int('000022d3f4210c9fb88d8da10a2f86d08d28700c2770a7481ac4fab072f31458', 16)
PREV_BLOCKHASH = 0
MINEDBLOCK_HEIGHT = 1
block_idpool = []

# Receive a new idblock before generate itself, store the old state to generate the same height
Generating_height = 1
Pool_isbackup = False
BACKMINING_TARGET = int('000022d3f4210c9fb88d8da10a2f86d08d28700c2770a7481ac4fab072f31458', 16)
BACKPREV_BLOCKHASH = 0
BACKMINEDBLOCK_HEIGHT = 1
BACK_POOL = []
BACKKEY_POOL = []

