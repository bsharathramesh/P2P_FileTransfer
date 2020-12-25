# from RFCIndex import RFCIndex
# from PeerServer import PeerServer
import os
import socket
import json
import traceback, sys
import threading
import platform
import re
import csv
import time

my_objects = []
file_list = []
file_name = []
path = "C:\\IP\\RFCS\\" 
location_of_file_path = "C:\\IP\\RFCS\\"
filepath1 = "C:\\IP\\ips.csv"
filepath = "C:\\IP\\ips.csv"
location_of_file_path.strip()



class pthread(threading.Thread):
    
    def __init__(self,socket,Client_IP):
        threading.Thread.__init__(self)
        self.lock=threading.Lock()
        print(self.lock)
        self.csocket=socket
        self.ip=Client_IP[0]
        self.socket=Client_IP[1]

    def run(self):
        print("Received connection request from:" + threading.currentThread().getName())
        recvMessage = self.csocket.recv(2048).decode('utf-8')
        print("The message which is received from client: ")
        print(recvMessage)
        if 'GetRFC' in recvMessage:
            data = recvMessage[recvMessage.index('GetRFC')+7:recvMessage.index('P2P-DI')]
            print(data)
            data = data.strip()
            #print(data)
            file1 = data + '.txt'
            print(file1)
            file1_path = location_of_file_path + '\\'+file1
            print(file1_path) 
            print(file_list)
            if file1 in file_name:
                print("File is present")
                fileSize = os.stat(file1_path).st_size
                print(fileSize)
                try:
                    f = open (file1_path,'rb')  # opening the file in the binary mode
                    #print
                except:
                    print("Sorry Unable to open to the file: %s",file1_path)
                    errorMessage = "404: Not Found"
                    self.csocket.send(errorMessage.encode('utf-8'))
                    self.csocket.close()
                    exit()

                x = f.read(2048)
                while (fileSize > 0):
                    self.csocket.send(x)
                    fileSize = fileSize - 2048
                    print(fileSize)
                    x = f.read(2048)
                    if((fileSize == 0) or (fileSize<0)):
                        f.close()
                print("Done with sending the file: %s",file1_path)
                self.csocket.close()

            else:
                print("Sorry File Not Found: ",file1_path)
                errorMessage = "404: Not Found"
                self.csocket.send(errorMessage.encode('utf-8'))
                self.csocket.close()
                exit()
                

        elif 'RFCQuery' in recvMessage:
            global filepath1
            # Reading the data from the csv file to determine the RFCs present in the system.
            list1 = []
            #filepath1 = "C:\\IP1\\ips.csv"
            with open(filepath1, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    list1.append(row)
            data = json.dumps(list1)
            send_response = 'POST 200 OK' + '<cr> <lf>\nFrom:' + socket.gethostname() + '<cr><lf>\nDate:' + str(time.asctime(time.localtime(time.time()))) + '<cr> <lf>\nData-Type: RFClist <cr> <lf>\n<cr> <lf>\n' + data
            print(send_response)
            self.csocket.send(send_response.encode())



def commmunicate_with_rs():
    #Create a socket Object
    
    hostinfo = []
    s = socket.socket()
    # Define the port and the URL/IP on which RS is listening
    port = 65432
    URL = '10.137.39.215'
    listening_port = int(global_listening_port)
    s.connect((URL,port))
    hostname = socket.gethostname()
    print("Your Computer Name is:" + hostname)      
    hostinfo.append(listening_port)

    
    
# Sub routing to get all the RFC files present in the current server.
def get_all_files(path):
    #file_list = []
    global filepath
    basepath = path
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = (s.getsockname()[0])
    print(ip)
    s.close()
    port = global_listening_port
    for entry in os.listdir(basepath):
        if os.path.isfile(os.path.join(basepath, entry)):
            #print ("asdfasdf")
            print(entry)
            fileName = entry + ';' + ip + ';' + port
            file_list.append(fileName)
    print(file_list)
    
    # writing all the files in the csv file
    #filepath = "C:\\IP1\\ips.csv"
    print("Storing the RFCs present in the local Server to: ",filepath)
    with open(filepath,'w', newline ='') as f:
        writer = csv.writer(f)
        for words in file_list:
            writer.writerow([words])
     


def get_all_files_names(path):
    #file_name = []
    basepath = path
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    port = global_listening_port
    for entry in os.listdir(basepath):
        if os.path.isfile(os.path.join(basepath, entry)):
            print(entry)
            file_name.append(entry)
    print(file_name)

Server_Thread = []
file_list = []
global_listening_port = input("Enter the listening port of the server: ")

def main():
    global path
    print("All the files in the present working directory:")
    #path = "C:\\IP1\\RFCS\\"
    get_all_files(path)
    print("All the files in the present working directory:")
    #path = "C:\\IP1\\RFCS\\"
    get_all_files_names(path)
    print(file_list) 
    
    Host = ''
    port = int(global_listening_port)
    Server_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Server_Socket.bind((Host,port))
    print ("socket binded to %s " %(port))

    while True:
        Server_Socket.listen(6)
        print('The Server Socket is listening')
        Client_Socket, Client_IP= Server_Socket.accept()
        print("Client_Socket: ",Client_Socket)
        print("Got the connection from Client_Socket: ",Client_IP)
        np=pthread(Client_Socket,Client_IP)
        np.start()
        Server_Thread.append(np) 
    
for st in Server_Thread:
	st.join()

main()