import socket    
import json   
#from classes.PeerServer import PeerServer  
#from classes.RFCIndex import RFCIndex  
import traceback, sys         
import os.path
import platform
import re
import types
import csv
import datetime
  
#Path to save and retreive RFCs
save_path = 'C:\\IP\\RFCS'
csv_save_path = 'C:\\IP\\ips.csv'
#List of all RFCs that will be requested
list_of_RFCS = [7500,7501,7502,7503,7504,7505,7506,7507,7508,7509,7510,7511,7512,7513,7514,7515,7516,7517,7518,7519,7520,500,501,503,504,505,506,507,508,509,510,511,512,513,514,515,516,517,518,519,520]
exisiting_files = []
hostname = socket.gethostname()
global_cookie = None
listening_port = None

port = 65432
URL = '10.152.22.185'

class PeerServer:
    rfcList = []
    ttl = 7200
    port = -1
    ip = ""
    cookie = -1
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

class RFCIndex:
    title = ""
    number = -1
    file = None
    ttl = 7200
    hostname = ""
    port = -1

    def __init__(self, title: str, number: int, file: str, ttl: int, hostname: str, port :int):
        self.title = title
        self.number = number
        self.file = file
        self.ttl = ttl
        self.hostname = hostname  
        self.port = port

def communicate_with_rs(rfc: int):
    global global_cookie
    global URL
    global port
    # send_TTL()
    # Create a socket object 
    s = socket.socket()          
    
    # Define the port and the URL/IP on which RS is listening  
    # port = 65432    

    # connect to the server on local computer 
    s.connect((URL, port)) 

    messageType = "PQuery"
    # cookie = '1'
    sendMessage = 'GET ' + messageType + ' P2P-DI/1.0 <cr> <lf>\nHost ' + hostname +' <cr> <lf>\nPort ' + str(port) +' <cr> <lf>\nCookie '+ global_cookie +' <cr> <lf>\nOperating System '+ str(platform.platform()) +' <cr> <lf>\n'
    # print(sendMessage)
    s.send(sendMessage.encode())
    # Received_MSG = s.recv(2048).decode()
    # print(Received_MSG)
    
    # receive data from the server 
    receivedData = s.recv(2048).decode()
    # print(receivedData)

    Received_MSG_arr = receivedData[receivedData.index('<cr> <lf>\n<cr> <lf>\n')+19:]
    #Received_MSG_arr = json.loads(Received_MSG)
    # print(Received_MSG_arr)
    # ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', Received_MSG_arr )
    # print(ip)
    # s.close()

    arr = json.loads(Received_MSG_arr)
    # print(arr)
    if(len(arr) == 0):
        print("No Peer Active!!")

    # close the connection 
    s.close()    
    for ele in arr:
        # print("____________________________________")
        # print(ele)
        node = PeerServer(**ele)
        try:
            if(communicate_with_peer(node, rfc)):
                break
        except Exception:
            traceback.print_exc(sys.stdout)
    if(len(arr) != 0):
        print("Checked with every node")

def communicate_with_peer(node: PeerServer, rfc: int):
    # Create a socket object 
    s = socket.socket()          
    
    # Define the port and the URL/IP on which RS is listening  
    port = int(node.port)
    URL = node.ip           

    # connect to the server on local computer 
    try:
        s.connect((URL, port)) 
    except (ConnectionRefusedError , OSError, Exception) as e:
        # traceback.print_exc(sys.stdout)
        print("Couldnot connect to host: " + URL + ":" + str(port))
        return False
        # pass
        # print(identifier)

    #RFC required
    messageType = 'RFCQuery '
    send_message = 'GET ' + messageType + 'RFC-Index' + ' P2P-DI/1.0 <cr> <lf>\n' + 'Host: ' + hostname + '<cr> <lf>\n' + 'OS: ' + str(platform.platform())
    # print(send_message)
    s.send(send_message.encode())
    
    receivedData = ''
    data =s.recv(32768).decode()
    receivedData = receivedData + data 
    # receive data from the server 
    # while True:
    #     print('receiving data...!!')
    #     data =s.recv(2048).decode()
    #     receivedData = receivedData + data 
    #     print('data=%s', (data))
    #     if not data:
    #         break
        
    #  = s.recv(2048).decode()
    # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    # print(receivedData)
    receivedData = receivedData[receivedData.index('<cr> <lf>\n<cr> <lf>\n')+20:]
    #if file is not found on the server
    if(receivedData == "[]"):
        arr = json.loads(receivedData)
    else:
        try:
            #Extracting host information
            # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            # print(receivedData)
            arr = json.loads(receivedData)
            for ele in arr:
                # print("##############################################")
                # print(ele)
                
                if type(ele) == type([]):
                    ele = ele[0]
                if ele.split(".")[0] == rfc:
                #trying to convert the recieved data to peer obj, if exception the data is file
                #rfc = RFCIndex(**receivedData)
                    #if(rfc.temp_hostname != ""):
                        #using recursion to call to next host
                    #   communicate_with_peer(PeerServer([], 7200, ip=rfc.hostname, port=rfc.port, cookie=-1))
                    #else:
                    try:
                        URL = ele.strip().split(";")[1]
                        port = ele.strip().split(";")[2]
                        
                        # print("*************************************")
                        # print(URL + ":"+port)
                        # print("*************************************")
                        # Create a socket object 
                        s1 = socket.socket()          
                        
                        # Define the port and the URL/IP on which RS is listening  
                        # port = node.port
                        # URL = node.ip           

                        # connect to the server on a different computer 
                        s1.connect((URL, int(port))) 
                        messageType = "GetRFC "
                        send_message = 'GET ' + messageType + str(rfc) + ' P2P-DI/1.0 <cr> <lf>\n' + 'Host: ' + hostname + '<cr> <lf>\n' + 'OS: ' + str(platform.platform())
                        s1.send(send_message.encode())
                        save_in_csv(rfc, URL, port)
                        receive_file(rfc, s1)
                        return True
                    except Exception:
                        traceback.print_exc(file=sys.stdout)
                    finally:
                        s1.close
        except Exception:
            #Saving the file
            print("exception occured: ")
            traceback.print_exc(file=sys.stdout)
        finally:
            s.close()
    # close the connection
    s.close()    
    return False

#Receive the file and store it in the path
def receive_file(rfc: RFCIndex, s: socket):
    d1 = datetime.datetime.now()
    #Absolute path at which file has to be stored
    completeName = os.path.join(save_path, str(rfc) + ".txt")
    #Oppening the file
    with open(completeName, 'wb') as f:
        print('file opened')
        #receiving file in multipart if it is big
        while True:
            print('receiving data...')
            data = s.recv(2048)
            # print('data=%s', (data))
            if not data:
                break
            # write data to a file
            f.write(data)
    f.close()
    d2 = datetime.datetime.now()
    print("++++++++++++++ File transfer took a time of " + str(d2-d1) + "++++++++++++++++++++++++")

def save_in_csv(RFC: int, ip: str, port: str):
    with open(csv_save_path, mode='a', newline ='') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        #way to write to csv file
        writer.writerow([str(RFC) +'.txt;' + ip + ';' + str(port)])

def send_registration():
    global global_cookie
    s2 = socket.socket()
    # sending the info to RS
    s2.connect((URL,port))
    messageType = "Register"

    cookie = 'None'
    listening_port = input("Enter Server port : ")
    if(global_cookie):
        cookie = str(global_cookie)

    sendMessage = 'GET ' + messageType + ' P2P-DI/1.0 <cr> <lf>\nHost ' + hostname +' <cr> <lf>\nPort ' + str(listening_port) +' <cr> <lf>\nCookie '+ cookie +' <cr> <lf>\nOperating System '+ str(platform.platform()) +' <cr> <lf>\n'
    # print(sendMessage)
    s2.send(sendMessage.encode())
    Received_MSG = s2.recv(2048).decode()
    # print(Received_MSG)
    Cookie = Received_MSG[Received_MSG.index('<cr> <lf>\n<cr> <lf>\n')+19:]
    # print (Cookie)
    global_cookie = Cookie
    # print(global_cookie)

def send_TTL():
    global global_cookie
    s2 = socket.socket()
    # sending the info to RS
    s2.connect((URL,port))
    messageType = "KeepAlive"

    print(global_cookie)
    sendMessage = 'GET ' + messageType + ' P2P-DI/1.0 <cr> <lf>\nHost ' + hostname +' <cr> <lf>\nPort ' + str(listening_port) +' <cr> <lf>\nCookie '+ str(global_cookie) +' <cr> <lf>\nOperating System '+ str(platform.platform()) +' <cr> <lf>\n'

    print(sendMessage)
    s2.send(sendMessage.encode())
    Received_MSG = s2.recv(2048).decode()
    print(Received_MSG)

def send_leave_message():
    global global_cookie
    s2 = socket.socket()
    # sending the info to RS
    s2.connect((URL,port))
    messageType = "Leave"

    sendMessage = 'GET ' + messageType + ' P2P-DI/1.0 <cr> <lf>\nHost ' + hostname +' <cr> <lf>\nPort ' + str(listening_port) +' <cr> <lf>\nCookie '+ str(global_cookie) +' <cr> <lf>\nOperating System '+ str(platform.platform()) +' <cr> <lf>\n'
    print(sendMessage)
    s2.send(sendMessage.encode())
    Received_MSG = s2.recv(2048).decode()
    print(Received_MSG)

def load_existing_files():
    global exisiting_files
    for r, d, f in os.walk(save_path):
        for file in f:
            if '.txt' in file:
                exisiting_files.append(file.split(".")[0])

load_existing_files()
# print(exisiting_files)

# send_leave_message()
inputParam = None
URL = input("Enter RS IP: ")
port = int(input("Enter RS port: "))
while(True):
    print("1. Register to RS")
    print("2. Request files")
    print("3. Keep Alive")
    print("4. Leave")
    inputParam = int(input("Enter your choice: "))
    if(inputParam == 1):
        send_registration()
    elif(inputParam == 2):
        print("_____________________Starting File Requests_________________________")
        d1 = d1 = datetime.datetime.now()

        list_rfcs = input("Enter the list of RFCs to request Comma seperated ")
        for rfc in list_rfcs.split(","):
            if rfc not in exisiting_files:
                rfc = rfc.strip()
                print(rfc)
                communicate_with_rs(rfc)
        d2 = datetime.datetime.now()
        print("______________________Total Time Elapsed is:" + str(d2-d1) +"________________________")
    elif(inputParam == 3):
        send_TTL()
    elif(inputParam == 4):
        send_leave_message()
    else:
        print("Invalid Input, Please try again")