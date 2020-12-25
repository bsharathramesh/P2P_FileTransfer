import socket
import time
import json


class Peer:
    t_c = 0
    def __init__(self, hname, port):
        self.hname = hname
        self.port = port
        self.next = None

    def initial(self,IP):
        Peer.t_c += 1
        self.c = Peer.t_c
        self.s_ip = IP
        self.flag = True
        self.ttl = 7200
        self.num = 1
        self.recent = time.asctime(time.localtime(time.time()))

    def update(self, IP):
        self.flag = True
        self.ttl = 7200
        self.s_ip = IP
        self.num += 1
        self.recent = time.asctime(time.localtime(time.time()))


class linked_list:
    def __init__(self):
        self.head = Peer(None, None)

    def append(self, hname, port, IP):
        new_node = Peer(hname, port)
        cur_node = self.head
        while cur_node.next != None:
            cur_node = cur_node.next
        cur_node.next = new_node
        cur_node.next.initial(IP)
        return cur_node.next.c

    def update(self,cookie, IP):
        cur_node = self.head
        while cur_node.next!= None:
            cur_node = cur_node.next
            if cur_node.c == int(cookie):
                cur_node.update(IP)

    def printev(self):
        cur_node = self.head
        while cur_node.next != None:
            cur_node = cur_node.next
            print(cur_node.hname, cur_node.s_ip, cur_node.port, cur_node.c, cur_node.flag, cur_node.recent, cur_node.num)

    #send active server list
    def send(self, IP):
        cur_node = self.head
        dlist= []
        d = {}
        while cur_node.next != None:
            cur_node = cur_node.next
            if (cur_node.flag == True and cur_node.s_ip != IP):
                d = {
                    'ip': cur_node.s_ip,
                    'port': cur_node.port
                }
                dlist.append(d.copy())
        return dlist

    #accpeting new connections
    def accept(self):
        request = connectionS.recv(1024).decode()
        arr = json.loads(request)
        plist.exists(arr[0],arr[1])
        connectionS.close()
        self.printev()

    #peer leaves the system
    def leave(self, Cookie):
        cur_node = self.head
        while cur_node.next!= None:
            cur_node = cur_node.next
            if (int(cur_node.c) ==int(Cookie)):
                cur_node.flag=False

    #peer keeps alive
    def KeepALive(self, Cookie):
        cur_node = self.head
        while cur_node.next!= None:
            cur_node = cur_node.next
            if (cur_node.c == int(Cookie)):
                cur_node.ttl = 7200

plist = linked_list()
serverP = 65432
serverS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverS.bind(('', serverP))
serverS.listen(5)   #max pending request = 5
print("Server is ready")
while True:
    connectionS, addr = serverS.accept()
    request = connectionS.recv(2048).decode()
    print('***************************REQUEST RECEIVED **************************')
    print(request)
    Host = request[request.index('Host') + 5:request.index(' <cr> <lf>\nPort')]  # extract the Host information
    Port = request[request.index('Port') + 5:request.index(' <cr> <lf>\nCookie')]  # extracts the port number
    Cookie = request[request.index('Cookie') + 7:request.index(' <cr> <lf>\nOperating')]  # get the cookie
    serverIP = addr[0]
    if 'Register' in request:
        if Cookie == 'None':
            Cookie = plist.append(Host, Port, serverIP)
         #    plist.printev()        print every peer who resgistered
        else:
            plist.update(Cookie, serverIP)
         #   plist.printev()

        send_Cookie = 'P2P-DI/1.0 200 OK' + '<cr> <lf>\nFrom:' + socket.gethostname() + '<cr><lf>\nDate:' + str(time.asctime(time.localtime(time.time()))) + '<cr> <lf>\nData-Type: Peer-Cookie <cr> <lf>\n<cr> <lf>\n' + str(Cookie)
        #print(send_Cookie)
        connectionS.send(send_Cookie.encode())
        connectionS.close()
        #print(Cookie)
    elif 'PQuery' in request:
        active_list = plist.send(serverIP)
        data = json.dumps(active_list)

        if len(active_list) > 0:
            send_Activelist = 'P2P-DI/1.0 200 OK' + '<cr> <lf>\nFrom:' + socket.gethostname() + '<cr><lf>\nDate:' + str(time.asctime(time.localtime(time.time()))) + '<cr> <lf>\nData-Type: Active Peer list <cr> <lf>\n<cr> <lf>\n' + data
         #   print(send_Activelist)
            connectionS.send(send_Activelist.encode())
            connectionS.close()
        else:
            send_Activelist = 'P2P-DI/1.0 404 No Active list' + '<cr> <lf>\nFrom:' + socket.gethostname() + '<cr><lf>\nDate:' + str(time.asctime(time.localtime(time.time()))) + '<cr> <lf>\nData-Type: Active Peer list <cr> <lf>\n<cr> <lf>\n' + data
        #    print(send_Activelist)
            connectionS.send(send_Activelist.encode())
            connectionS.close()


    elif 'Leave' in request:
        plist.leave(Cookie)
        send_Leave = 'P2P-DI/1.0 200 OK' + '<cr> <lf>\nFrom:' + socket.gethostname() + '<cr><lf>\nDate:' + str(time.asctime(time.localtime(time.time()))) + '<cr> <lf>\nData-Type: None <cr> <lf>\n<cr> <lf>\n' + 'Leave successful'
     #   print(send_Leave)
        connectionS.send(send_Leave.encode())
        connectionS.close()
     #   plist.printev()

    elif 'KeepAlive' in request:
        plist.KeepALive(Cookie)
        send_Keepalive = 'P2P-DI/1.0 200 OK' + '<cr> <lf>\nFrom:' + socket.gethostname() + '<cr><lf>\nDate:' + str(time.asctime(time.localtime(time.time()))) + '<cr> <lf>\nData-Type: None <cr> <lf>\n<cr> <lf>\n' + 'TTL update successful'
     #   print(send_Keepalive)
        connectionS.send(send_Keepalive.encode())
        connectionS.close()
     #   plist.printev()



