from flask import Flask, render_template, request, redirect
from markupsafe import escape
import socket
import sys
import os
import datetime
from threading import Thread
from cryptography.fernet import *
import struct
import numpy as np
import requests

# This class is created to return value from the thread
class Threadvalue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return
    
def func(h,p,cid,a,file,fname,metadata):   # Function defined for multi threading
    
    HOST = h  # The server's IP address
    PORT = p        # The port used by the server
    
    compdata = bytearray()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket type object is created 
    connected = False
    while not connected:
        try:
            s.connect((HOST, PORT))  # Connection with the server is bulid
            connected = True
        except Exception as e:
            print('Waiting for SP...')
            print("")
    print('Connected to SP: ', p)
    print("")
    '''
    size=s.recv(4)
    s1=int.from_bytes(size,'big')
    buff=s.recv(s1)
    print('Server: '+buff.decode())
    '''
    # requesting Metadata
    size=len('b')  
    s.sendall(size.to_bytes(4,'big'))
    s.sendall('b'.encode())
    
    # Initial data is being transfered 
    size=len(cid)  
    s.sendall(size.to_bytes(4,'big'))
    s.sendall(cid.encode())
#     print("Size cid:" , size)
    
    size=s.recv(4)
    s1=int.from_bytes(size,'big')
    sid = s.recv(s1)
    sid = sid.decode()
    print("ServerID: ",sid)
#     print("Serverid size: ",s1)
    print("")
    size=len(fname)
    s.sendall(size.to_bytes(4,'big'))
    s.sendall(fname.encode())
    filelist={}
    while True:
        size=len(a)
        s.sendall(size.to_bytes(4,'big'))
        s.sendall(a.encode())
        
        # uploading process 
        if (a=='2'):   
            size=len(file[0])
            s.sendall(size.to_bytes(4,'big'))
            s.sendall(file[0])
#             print("1. ", file[0])
#             print("1 size:" , size)
            
            junk=s.recv(3)
#             print(junk.decode())
            
            size=len(file[1])
            s.sendall(size.to_bytes(4,'big'))
            s.sendall(file[1])
#             print("2. ",file[1])
#             print("2. size:",size)
            
            # uploading Metadata
            size=len(metadata)
            s.sendall(size.to_bytes(4,'big'))
            s.sendall(metadata)
#             print("2. ",metadata)
#             print("2. size:",size)
            print("Shards sent to: ", p)
            break
        
        # Downloading process 
        elif (a == '1'):
            shardid=[]
            data=b''
#             print(file)
            for i in range(len(file)):
                serverid= file[i]
                if(serverid[0]==sid):
                    shardid.append(serverid[2])
            size=len(shardid)
            s.sendall(size.to_bytes(4,'big'))
            for i in range(len(shardid)):
                size=len(shardid[i])
                s.sendall(size.to_bytes(4,'big'))
                s.sendall(shardid[i].encode())
                #print(shardid[i])
                size=s.recv(4)
                s1=int.from_bytes(size,'big')
                buff=b''
                while len(buff) < s1 :
                    buff += s.recv(s1)
                data=data+buff
            #print(data)
            s.close()
            return data
        
        else:
            continue

def func2(h,p,cid,a):
    
    HOST = h  # The server's IP address
    PORT = p        # The port used by the server
    
    compdata = bytearray()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket type object is created 
    connected = False
    while not connected:
        try:
            s.connect((HOST, PORT))  # Connection with the server is bulid
            connected = True
        except Exception as e:
            print('Waiting for SP connection...')
            print("")
    print('Connected to Server: ', HOST, ": ", PORT)
    print("")
    '''
    size=s.recv(4)
    s1=int.from_bytes(size,'big')
    buff=s.recv(s1)
    print('Server: '+buff.decode())
    '''
    # requesting Metadata
    size=len('a')  
    s.sendall(size.to_bytes(4,'big'))
    s.sendall('a'.encode())
    
    
    # Initial data is being transfered 
    size=len(cid)  
    s.sendall(size.to_bytes(4,'big'))
    s.sendall(cid.encode())
#     print("Size cid:" , size)
    
    size=s.recv(4)
    s1=int.from_bytes(size,'big')
    Metadata1 = s.recv(s1)
    Metadata1 = Metadata1.decode()
    
    
#     print(Metadata1)
    s.close()
#     print(172)
    return Metadata1


###### Main
h='127.0.0.1'
h1='127.0.0.1'
h2='127.0.0.1'
p=65432
p1=65433
p2=65434

app = Flask(__name__)

cid ='13' # input('Enter client ID.')
root= os.getcwd()

namelist=[]
flist=[]
file=''

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/upload')
def upload():
    return render_template('upload.html')
@app.route('/download')
def download():
    os.chdir(root)
    a='1'
    # Getting metadata
    # Multi Threading is used to connect with multiple servers in paralel 
    x=Threadvalue(target=func2, args =(h,p,cid,a))
    y=Threadvalue(target=func2, args=(h1,p1,cid,a))
    z=Threadvalue(target=func2, args=(h2,p2,cid,a))
    x.start()
    Metadata1=x.join()
    y.start()
    Metadata2=y.join()
    z.start()
    Metadata3=z.join()
    
    global flist
    global namelist
    global file
    flist = []
    namelist = []
    # Metadata is accessed 
#         filename=cid+'.txt'
#         f=open(filename,'r')
#         size=os.path.getsize(filename)
#         file=f.read(size)
#         f.close()
    encfile = Metadata1.encode()
    print('Type Metadata received :',type(encfile))
    print("")
    if (Metadata1 == 'no'):
        namelist = ['No Data uploaded']
    else:
        
        # Decrypt Metadata
        # Decrypt Metadata
        f=open(cid+' key.txt','rb')
        size=os.path.getsize(cid+' key.txt')
        key3=f.read(size)
        fernet= Fernet(key3)
        file1= fernet.decrypt(encfile)  # Decryption of file 
        print('Metadata file received: ', type(file))
        file = file1.decode()
        print(file)
        print("")
        
        filelist=file.split('#\n')
        filelist.remove('')
        #print(filelist)
        print('Select from the following list of files.')
        for i,j in enumerate(filelist):
            temp=j.split('\n')
    #         print('333',temp)
            #if(i!=0):
            print(i+1,' ',temp[0])
            namelist.append(temp[0])
            flist.append(temp)
            flist[i].remove(temp[0])
            flist[i].remove('')
            flist[i].remove(temp[0])
    #     print(flist)
        
    return render_template('download.html', posts=namelist)


@app.route('/submitup', methods=['POST'])
def uploading():
    os.chdir(root)
    a='2'
    # Getting metadata
    # Multi Threading is used to connect with multiple servers in paralel
    x=Threadvalue(target=func2, args =(h,p,cid,a))
    y=Threadvalue(target=func2, args=(h1,p1,cid,a))
    z=Threadvalue(target=func2, args=(h2,p2,cid,a))
    x.start()
    Metadata1=x.join()
    y.start()
    Metadata2=y.join()
    z.start()
    Metadata3=z.join()
#     print(210)
    filepath = request.form["content"]
    print("File Name to be uploaded: ", filepath)
    print("")
#     print(type(filepath))
    key = Fernet.generate_key()  # Encryption Key is generated 
    fernet= Fernet(key)
    f=open(filepath,'rb')
    size=os.path.getsize(filepath)
    file = f.read(size)  # File to be uploaded is read 
    f.close()
    
    encfile= fernet.encrypt(file)  # File is encrypted 
    
    fsize=len(encfile)
    print("Encrypted File:", encfile)
#     print("size of Encrypted file:",fsize)
    print("")
    # Sharding process 
    if(fsize%6==0):
        chunksize= fsize//6
    else:
        chunksize= fsize//6+1
    
#     print("Chunksize:" , chunksize)
    shards = [encfile[i:i+chunksize] for i in range(0,fsize,chunksize)]
    print("Shards produced: ")
    print(shards)
    print("")
    arr = np.array(shards)
    newarr = np.array_split(arr, 3)
    print("Array[0]:" ,newarr[0])
    print("Array[1]:" ,newarr[1])
    print("Array[2]:" ,newarr[2])
    print("")
#     print('230',type(Metadata1))
#     print('231',type(filepath))
    # Metadata is created
    if Metadata1 == 'no':
        
        Metadata1 = '#\n'
        Metadata1+=filepath
        Metadata1+='\n'
        Metadata1+=key.decode()
        Metadata1+='\n'
        k=1;
        for i in range(3):
            for j in range(int(len(shards)/3)):
                wr=str(i)+','+str(k)
                k=k+1
                Metadata1+=wr
                Metadata1+='\n'
    else:
        if (Metadata1.find(filepath) == -1):
            # Decrypt Metadata
            f=open(cid+' key.txt','rb')
            size=os.path.getsize(cid+' key.txt')
            Metakey=f.read(size)
            fernet= Fernet(Metakey)
            Metadata1= fernet.decrypt(Metadata1.encode()).decode()  # Decryption of file 
#             print("File 336:")
#             print(file)
#             print("")
            Metadata1+='#\n'
            Metadata1+=filepath
            Metadata1+='\n'
            Metadata1+=key.decode()
            Metadata1+='\n'
            k=1;
            for i in range(3):
                for j in range(int(len(shards)/3)):
                    wr=str(i)+','+str(k)
                    k=k+1
                    Metadata1+=wr
                    Metadata1+='\n'
        else:
            print('File already exists')
            print("")
            exitt=1
    
#         filename=cid+'.txt'
#         if (not(os.path.exists(filename))):
#             f=open(filename,'a+')
#             f.write('#\n')
#             f.write(filepath)
#             f.write('\n')
#             f.close()
#             f=open(filename,'ab')
#             f.write(key)
#             f.write(bytes('\n','utf-8'))
#             f.close()
#             f=open(filename,'a+')
#             k=1;
#             for i in range(3):
#                 for j in range(int(len(shards)/3)):
#                     wr=str(i)+','+str(k)
#                     k=k+1
#                     f.write(wr)
#                     f.write('\n')
#             f.close()
#         else:
#             f=open(filename,'r+')
#             size=os.path.getsize(filename)
#             print('size',size)
#             filedata = f.read(size)
#             print(len(filedata))
#             if (filedata.find(filepath) == -1):
#                 f.write('#\n')
#                 f.write(filepath)
#                 f.write('\n')
#                 f.close()
#                 f=open(filename,'ab')
#                 f.write(key)
#                 f.write(bytes('\n','utf-8'))
#                 f.close()
#                 f=open(filename,'a+')
#                 k=1;
#                 for i in range(3):
#                     for j in range(int(len(shards)/3)):
#                         wr=str(i)+','+str(k)
#                         k=k+1
#                         f.write(wr)
#                         f.write('\n')
#                 f.close()
#             else:
#                 print('File already exists')
#                 exitt=1
#         if(exitt==1):
#             continue
    
    # Reading metadata file to upload on blockchain
#         f=open(filename,'rb')
#         size=os.path.getsize(filename)
#         print('size',size)
    metadata = Metadata1
    print("Metadata: ")
    print(metadata)
    print("")
    # Encrypting Metadata
    Metakey2 = Fernet.generate_key()  # Encryption Key is generated 
    fernet= Fernet(Metakey2)
    print('key ',Metakey2)
    print("")
    metadata = fernet.encrypt(metadata.encode())
    print(type(metadata))
    
    # Saving key in file
    f=open(cid+' key.txt','wb')
    f.write(Metakey2)
    f.close()
    
    # Multi threading used to connect with multiple servers 
    x=Threadvalue(target=func, args =(h,p,cid,a,newarr[0],filepath,metadata))  
    y=Threadvalue(target=func, args=(h1,p1,cid,a,newarr[1],filepath,metadata))
    z=Threadvalue(target=func, args=(h2,p2,cid,a,newarr[2],filepath,metadata))
    x.start()
    x.join()
    y.start()
    y.join()
    z.start()
    z.join()
    
    return redirect('/')

@app.route('/submitdown', methods=['POST'])
def downloading():
    a='1'
    b = request.form["content"]
    global flist
    global namelist
    global file
    
    
    metadata=''
    # Multi Threading is used to connect with multiple servers in paralel 
    x=Threadvalue(target=func, args =(h,p,cid,a,flist[int(b)-1],namelist[int(b)-1],metadata))
    y=Threadvalue(target=func, args=(h1,p1,cid,a,flist[int(b)-1],namelist[int(b)-1],metadata))
    z=Threadvalue(target=func, args=(h2,p2,cid,a,flist[int(b)-1],namelist[int(b)-1],metadata))
    x.start()
    data1=x.join()
    y.start()
    data2=y.join()
    z.start()
    data3=z.join()
    '''
    temp1=''.join([str(i) for i in data1])
    temp2=''.join([str(i) for i in data2])
    temp3=''.join([str(i) for i in data3])
    '''
    # Data shards are joined together 
    data= data1+data2+data3
    
#         f=open(filename,'rb')
#         size=os.path.getsize(filename)
#         file=f.readlines(size)
#         f.close()
#     print(404,file)
    file = file.encode()
#     print(405,file)
    file = file.split(bytes('\n','utf-8'))
#     print(407,file)
    j=0
    for i,k in enumerate(file):
#         print(k.decode())
        if(k.decode()=='#'):
            j=j+1
#             print('j=',j)
            if(j==int(b)):
                keyy=file[i+2]  # Key is read from the metadata for decryption 
#                 print('b')
    #ke=bytes(keyy,'base64')
    key=keyy
    print("Key used to decrypt downloaded file: ")
    print(key)
    print("")
    #filelist=file.split('#\n')
    print("Encrypted Data: ")
    print(data)
    print("")
#     print(type(data))
    fernet= Fernet(key)
    decfile= fernet.decrypt(data)  # Decryption of file 
    print("File received after decrypting: ")
    print(decfile)
    
    # Decrypted file stored into the PC 
    folder=datetime.datetime.now().date()
    curfol= os.getcwd()
    a,c=os.path.split(curfol)
    if (not(os.path.exists(str(folder))) and c!=str(folder)):
            os.mkdir(str(folder))
    
    if(c!=str(folder)):
        os.chdir(str(folder))
#     print(namelist[int(b)-1])
    
    f=open(namelist[int(b)-1],'wb')
    f.write(decfile)
    f.close()

    return redirect('/')

app.run(debug=True, port=5001)