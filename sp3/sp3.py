import socket
import time
import sys
import os
import threading

from hashlib import sha256
import json
import time

from flask import Flask, request
import requests
from queue import Queue
import pickle

metaque = Queue()
bq = Queue()

# Blockchain code
class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    difficulty = 2

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []

    def create_genesis_block(self):
        genesis_block = Block(0, [], 0, "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if previous_hash == block.compute_hash():
            return False
        
        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    @staticmethod
    def proof_of_work(block):
        block.nonce = 0
        print("Block type in POW: ", type(block))
                                          
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def mine(self):
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)
        #print new block
        print("New Block")
        print(new_block.__dict__)
        print("Type New Block : ", type(new_block))
        
        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)

        self.unconfirmed_transactions = []

        return True

# app = Flask(__name__)

blockchain = Blockchain()
blockchain.create_genesis_block()

peers = set()

Port=12343
#@app.route('/new_transaction', methods=['POST'])
def new_transaction(tx_data):
#     tx_data = request.get_json()
#     required_fields = ["author", "content"]
# 
#     for field in required_fields:
#         if not tx_data.get(field):
#             return "Invalid transaction data", 404
# 
#     tx_data["timestamp"] = time.time()

    blockchain.add_new_transaction(tx_data)

#     return "Success", 201


#@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
#     return json.dumps({"length": len(chain_data),
#                        "chain": chain_data,
#                        "peers": list(peers)})
    print({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)})

#@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions(chain):
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    else:
        chain_length = len(blockchain.chain)
        consensus(chain)
#         if chain_length == len(blockchain.chain):
#             announce_new_block(blockchain.last_block)
#         return "Block #{} is mined.".format(blockchain.last_block.index)
        return chain_length

#@app.route('/register_node', methods=['POST'])
def register_new_peers():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    peers.add(node_address)

    return get_chain()


#@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        announce_peer()
        return "Registration successful", 200
    else:
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block()
    for idx, block_data in enumerate(chain_dump):
        if idx == 0:
            continue  
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["nonce"])
        proof = block_data['hash']
        added = generated_blockchain.add_block(block, proof)
        if not added:
            raise Exception("The chain dump is tampered!!")
    return generated_blockchain


#@app.route('/add_block', methods=['POST'])
def verify_and_add_block(block_data):
#     block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


#@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


def consensus(chain):
    global blockchain

#     longest_chain = None
#     current_len = len(blockchain.chain)
    if len(chain) > len(blockchain.chain) and blockchain.check_chain_validity(chain):
        blockchain = bchain
        return True
#     for node in peers:
#         response = requests.get('{}chain'.format(node))
#         length = response.json()['length']
#         chain = response.json()['chain']
    
#     if length > current_len and blockchain.check_chain_validity(chain):
#         current_len = length
#         longest_chain = chain
# 
#     if longest_chain:
#         blockchain = longest_chain
#          return True

    return False


# def announce_new_block(block):

#     for peer in peers:
#         url = "{}add_block".format(peer)
#         headers = {'Content-Type': "application/json"}
#         requests.post(url,
#                       data=json.dumps(block.__dict__, sort_keys=True),
#                       headers=headers)

#@app.route('/update_peers', methods=['POST'])
def update_peer_list():
    newport = request.get_json()
    addr = "http://127.0.0.1:" + str(newport)+'/'
    peers.add(addr)
    return addr

def announce_peer():
    for peer in peers:
        url = "{}update_peers".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(Port, sort_keys=True),
                      headers=headers)
        
#app.run(debug=True, port=Port)

#Socket programing Network 
def func(x,y):
    conn=x
    addr=y
    sid='2'
    curdir=os.getcwd()
    with conn:
        print('Connected by', addr)
        '''
        size=sys.getsizeof('Welcome to File Server')
        conn.sendall(size.to_bytes(4,'big'))
        conn.sendall(b'Welcome to File Server')
        '''
        # getting request 
        size=conn.recv(4)
        s1=int.from_bytes(size,'big')
        check = conn.recv(s1)
        check = check.decode()
        
        if check == 'a':
            # receiving ClientId 
            size=conn.recv(4)
            s1=int.from_bytes(size,'big')
            clientid = conn.recv(s1)
            clientid = clientid.decode()
            print("clientid: ",clientid)
            print("clientid size: ",s1)
            
            Metadata1 = 'no'
            
            for block in reversed(blockchain.chain):
                if block.transactions:
                    if block.transactions[0]["CId"] == clientid:
                        Metadata1 = block.transactions[0]["Metadata"]
                        break
                        
            size=len(Metadata1)  
            conn.sendall(size.to_bytes(4,'big'))
            conn.sendall(Metadata1.encode())
                   
                
            conn.close()
        
            return True
        
        size=conn.recv(4)
        s1=int.from_bytes(size,'big')
        clientid = conn.recv(s1)
        clientid = clientid.decode()
        print("clientid: ",clientid)
        print("clientid size: ",s1)
        
        size=len(sid)
        conn.sendall(size.to_bytes(4,'big'))
        conn.sendall(sid.encode())
        print("Size sid:" , size)
        buff=conn.recv(4)
        s1=int.from_bytes(buff,'big')
        fname=conn.recv(s1)
        
        size=conn.recv(4)
        s1=int.from_bytes(size,'big')
        buff=conn.recv(s1)
        print('a:'+buff.decode())
        
        if (buff.decode()=='2'):
            size=conn.recv(4)
            s1=int.from_bytes(size,'big')
            print('s',s1)
            buff=b''
            while len(buff) < s1:
                 buff += conn.recv(s1)
            print(buff)
            
            conn.sendall('abc'.encode())
            
            size=conn.recv(4)
            s1=int.from_bytes(size,'big')
            print('s',s1)
            buff1=b''
            while len(buff1) < s1:
                 buff1 += conn.recv(s1)
            print(buff1)
            
            # Receiving metadata file
            size=conn.recv(4)
            s1=int.from_bytes(size,'big')
            print('s',s1)
            metadata=b''
            while len(metadata) < s1:
                 metadata += conn.recv(s1)
            
            # metadata dictionary
            metaDict = {"CId": clientid, "Metadata": metadata.decode()}
            
            metaque.put(metaDict)
            print(metaDict)
            
            curfol= os.getcwd()
            if (not(os.path.exists(clientid)) and curfol!=clientid):
                os.mkdir(clientid)
            if(curfol!=clientid):
                os.chdir(clientid)
            
            # Creating Metadata file
            f=open("metadata.txt",'wb')
            f.write(metadata)
            f.close()
            
            curfol= os.getcwd()
            if (not(os.path.exists(fname)) and curfol!=fname):
                os.mkdir(fname)
            if(curfol!=fname):
                os.chdir(fname)
                
            
            filname='5.txt'
            f=open(filname,'wb')
            f.write(buff)
            f.close()
            filname='6.txt'
            f=open(filname,'wb')
            f.write(buff1)
            f.close()
            
            '''
            filelist = os.listdir("C:\FileServer\\")
            size = len(filelist)
            conn.sendall(size.to_bytes(4,'big'))
            for i in filelist:
                size = sys.getsizeof(i)
                conn.sendall(size.to_bytes(4,'big'))
                conn.sendall(i.encode())
                tosend=os.path.getsize("C:\FileServer\\"+i)
                conn.sendall(tosend.to_bytes(4,'big'))
            
            size=sys.getsizeof('Choose the file from the list above.\n\tEnter the serial number of the file you want to download.')
            conn.sendall(size.to_bytes(4,'big'))
            conn.sendall(b'Choose the file from the list above.\n\tEnter the serial number of the file you want to download.')
            '''    
        elif (buff.decode()=='1'):
            curfol= os.getcwd()
            if(curfol!=clientid):
                os.chdir(clientid)
            
            curfol= os.getcwd()
            if(curfol!=fname):
                os.chdir(fname)
            
            size=conn.recv(4)
            sh=int.from_bytes(size,'big')
            for i in range(sh):
                buff=conn.recv(4)
                s1=int.from_bytes(buff,'big')
                buff=conn.recv(s1)
                print('b',buff.decode())
                filename=buff.decode()+'.txt'
                f=open(filename,'rb')
                fsend=f.read()
                f.close()
                size = len(fsend)
                conn.sendall(size.to_bytes(4,'big'))
                conn.sendall(fsend)
                #conn.close()
                #break
            '''
            curfol= os.getcwd()
            a,b=os.path.split(curfol)
            if (not(os.path.exists(str(clientid))) and b!=str(clientid)):
                    os.mkdir(str(clientid))
            
            if(b!=str(folder)):
                os.chdir(str(clientid))
    
            '''
            
        elif(buff.decode()=='0'):
            conn.close()
        '''
        else:
            continue
        size=conn.recv(4)
        s1=int.from_bytes(size,'big')
        buff=conn.recv(s1)
        print('client:'+buff.decode())
        if buff.decode() == 'bye':
            conn.close()
            break
        
        filename=buff.decode()
        f=open("C:\FileServer\\"+filename,'rb')
        size=os.path.getsize("C:\FileServer\\"+filename)
        tosend=f.read(size)
        f.close()
        conn.sendall(size.to_bytes(4,'big'))
        conn.sendall(tosend)
        '''
        conn.close()

def funcserver(x,y):
    conn=x
    addr=y
    with conn:
        print('Connected by', addr)
        # sending blockchain
        data = pickle.dumps(blockchain)
        size = sys.getsizeof(data)
        conn.sendall(size.to_bytes(4,'big'))
        conn.sendall(data)
        
        
        while True:
            if metaque.empty():
                pass
            else:
                # adding new transaction
                print("Printing Uncomfirmed Transactions: ", blockchain.unconfirmed_transactions)
                tx= metaque.get()
                new_transaction(tx)
                
                print("Transaction: ", tx)
                print(blockchain.unconfirmed_transactions)
                # requesting chain
                size=len('send chain')
                conn.sendall(size.to_bytes(4,'big'))
                conn.sendall('send chain'.encode())
                
                # reveiving chain
                size=conn.recv(4)
                s1=int.from_bytes(size,'big')
                bchain=Blockchain()
                bchain = conn.recv(s1)
                bchain = pickle.loads(bchain)
                
                #printing blockchain
                chain_data=[]
                for block in bchain.chain:
                    chain_data.append(block.__dict__)
                print({"length": len(chain_data),
                                   "chain": chain_data,
                                   "peers": list(peers)})
                         
                # mining new block 
                chain_length = mine_unconfirmed_transactions(bchain.chain)
                
                # announcing to add block
                print("Block to Announce: ", blockchain.last_block.__dict__)

                if chain_length == len(blockchain.chain):
                    check = '1'
                    size = len(check)
                    conn.sendall(size.to_bytes(4,'big'))
                    conn.sendall(check.encode())
                    
                    lblock = blockchain.last_block
                    data = pickle.dumps(lblock)
                    size = sys.getsizeof(data)
                    conn.sendall(size.to_bytes(4,'big'))
                    conn.sendall(data)
                else:
                    check = '2'
                    size = sys.getsizeof(check)
                    conn.sendall(size.to_bytes(4,'big'))
                    conn.sendall(check.encode())
 
 
 
def storage():
    HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
    PORT = 65434        # Port to listen on (non-privileged ports are > 1023)
    curdir=os.getcwd()

    buff = b''
    buff1=b''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(5)
        while True:
            os.chdir(curdir)
            print('ready to accept')
            conn, addr = s.accept()
            x=threading.Thread(target=func, args=(conn,addr))
            x.start()
            
def blocknetserver():
    HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
    PORT = 65444        # Port to listen on (non-privileged ports are > 1023)
    curdir=os.getcwd()

    buff = b''
    buff1=b''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(5)
        #app.run(debug=True, port=Port)
        while True:
            os.chdir(curdir)
            print('ready to accept')
            conn, addr = s.accept()
            global peers
            peers.add(addr) # adding new peers 
            
            x=threading.Thread(target=funcserver, args=(conn,addr))
            x.start()

def blocknetclient(p):
    HOST = '127.0.0.1' # The server's IP address
    PORT = p        # The port used by the server
    
    compdata = bytearray()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket type object is created 
    connected = False
    while not connected:
        try:
            s.connect((HOST, PORT))  # Connection with the server is bulid
            connected = True
        except Exception as e:
            pass #Do nothing, just try again
#     s.connect((HOST, PORT))
    print('connected to server ',p)
    
    # recieving blockchain
    size=s.recv(4)
    s1=int.from_bytes(size,'big')
    bchain=Blockchain()
    bchain = s.recv(s1)
    bchain = pickle.loads(bchain)
    chain_data=[]
    for block in bchain.chain:
        chain_data.append(block.__dict__)
    global blockchain
    print(type(blockchain))
    print({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)})
    
    if len(bchain.chain) > len(blockchain.chain) and bchain.check_chain_validity(bchain.chain):
        blockchain = bchain


    while True:
        
        # getting request
        size=s.recv(4)
        s1=int.from_bytes(size,'big')
        junkdata = s.recv(s1)
        junkdata = junkdata.decode()
        print("request from server: ",junkdata)
        
        # sending chain 
        data = pickle.dumps(blockchain)
        size = sys.getsizeof(data)
        s.sendall(size.to_bytes(4,'big'))
        s.sendall(data)
        
        # recieving check
        size=s.recv(4)
        s1=int.from_bytes(size,'big')
        check = s.recv(s1)
        check= check.decode()
        
        if check == '1':
            # recieving last block
            size=s.recv(4)
            s1=int.from_bytes(size,'big')
            #lblock=Block()
            lblock = s.recv(s1)
            lblock = pickle.loads(lblock)
            print(type(lblock))
            print("lastblock received: ",lblock.__dict__)
            verify_and_add_block(lblock.__dict__)
        
        # printing final blockchain after mining
        print("Blockchain after mining new block")
        chain_data=[]
        for block in blockchain.chain:
            chain_data.append(block.__dict__)
        print({"length": len(chain_data),
                           "chain": chain_data,
                           "peers": list(peers)})
        
    
    
##################  Main ##############    
x=threading.Thread(target=storage, args=())
x.start()
y=threading.Thread(target=blocknetserver, args=())
y.start()

iplist=[65442,65443]

for i in iplist:
    z=threading.Thread(target=blocknetclient, args=(i,))
    z.start()
