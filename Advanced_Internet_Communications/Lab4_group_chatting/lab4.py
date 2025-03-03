#!/usr/bin/env python3
#Group8 - Hengbo Huang - Yinwen Xu
########################################################################

import socket
import argparse
import sys
import time
import struct
import ipaddress
import os 
import threading
import time
########################################################################
# Multicast Address and Port
########################################################################

#MULTICAST_ADDRESS = "239.0.0.10"
MULTICAST_ADDRESS = "239.0.0.10"
MULTICAST_PORT    =  2000

# Make them into a tuple.
MULTICAST_ADDRESS_PORT = (MULTICAST_ADDRESS, MULTICAST_PORT)

# Ethernet/Wi-Fi interface address
IFACE_ADDRESS = "192.168.2.12"



########################################################################
# Multicast Receiver 
########################################################################
#
# There are two things that we need to do:
#
# 1. Signal to the os that we want a multicast group membership, so
# that it will capture multicast packets arriving on the designated
# interface. This will also ensure that multicast routers will forward
# packets to us. Note that multicast is at layer 3, so ports do not
# come into the picture at this point.
#
# 2. Bind to the appopriate address/port (L3/L4) so that packets
# arriving on that interface will be properly filtered so that we
# receive packets to the designated address and port.
#
#########################################
# IP add multicast group membership setup
#########################################
#
# Signal to the os that you want to join a particular multicast group
# address on specified interface. Done via setsockopt function call.
# The multicast address and interface (address) are part of the add
# membership request that is passed to the lower layers.
#
# This is done via MULTICAST_ADDRESS from above and RX_IFACE_ADDRESS
# defined below.
#
# If you choose "0.0.0.0" for the Rx interface, the system will select
# the interface, which will probably work ok. In more complex
# situations, where, for example, you may have multiple network
# interfaces, you may have to specify the interface explicitly by
# using its address, as shown in the examples below.

# RX_IFACE_ADDRESS = "0.0.0.0"
# RX_IFACE_ADDRESS = "127.0.0.1"
RX_IFACE_ADDRESS = IFACE_ADDRESS 

##############################################
# Multicast receiver bind (i.e., filter) setup
##############################################
#
# The receiver socket bind address. This is used at the IP/UDP level to
# filter incoming multicast receptions. Using "0.0.0.0" should work
# ok. Binding using the unicast address, e.g., RX_BIND_ADDRESS =
# "192.168.1.22", fails (Linux) since arriving packets don't carry this
# destination address.
# 

# RX_BIND_ADDRESS = MULTICAST_ADDRESS # Ok for Linux/MacOS, not for Windows 10.
RX_BIND_ADDRESS = "0.0.0.0"

# Receiver socket will bind to the following.
RX_BIND_ADDRESS_PORT = (RX_BIND_ADDRESS, MULTICAST_PORT)

########################################################################

class Server:
    HOSTNAME = "0.0.0.0"      # All interfaces.
    RECV_SIZE = 256
    # Server port to bind the listen socket.
    PORT = 50000
    
    RECV_BUFFER_SIZE = 1024 # Used for recv.
    MAX_CONNECTION_BACKLOG = 10

    # We are sending text strings and the encoding to bytes must be
    # specified.
    # MSG_ENCODING = "ascii" # ASCII text encoding.
    MSG_ENCODING = "utf-8" # Unicode text encoding.

    # Create server socket address. It is a tuple containing
    # address/hostname and port.
    SOCKET_ADDRESS = (HOSTNAME, PORT)
    
    
    def __init__(self):
        #print("Bind address/port = ", RX_BIND_ADDRESS_PORT)
        #self.create_listen_socket()
        self.name = ""
        self.muticast_address = "239.0.0.10"
        self.port = 2000
        self.client_list=[]
        self.n = 1;
        self.dir_list = {}
        self.get_socket()
        self.getmes()

        
        
        # self.connect_CRDS()

    def getmes(self):
        self.mes, address_port = self.socket.recvfrom(Server.RECV_SIZE)
        adress, port = address_port
        client =  int(port)
        self.mes = self.mes.decode(Server.MSG_ENCODING)
        if (client in self.client_list ):
            self.connect_CRDS(address_port)
        else:
            self.client_list.append(client)
            self.n = self.n+1
            self.threads(address_port)



    def connect_CRDS(self,address_port,):
        # self.mes, address_port = self.socket.recvfrom(Server.RECV_SIZE)
        # self.mes = self.mes.decode(Server.MSG_ENCODING)
        # print("Received1: {} {}".format(self.mes, address_port))
        
        if( self.mes == "connect"):
            text = ("Connected to CRDS, Please enter your command, command list: getdir,makeroom,deleteroom and quit")
            text = text.encode("utf-8")
            self.socket.sendto(text, address_port)
            self.CRDS(address_port)
        elif(self.mes in self.dir_list):
            self.check_room()
        else:
            self.getmes()


    def CRDS(self, address_port):
        self.data, address_portc = self.socket.recvfrom(Server.RECV_SIZE)
        adress, port = address_portc
        client = int(port)
        print("Received2: {} {}".format(self.data.decode('utf-8'), address_portc))
        self.data = self.data.decode('utf-8')
        if (client not in self.client_list ):
            print("create new thread")
            self.client_list.append(client)
            self.n = self.n+1
            self.threads(address_portc)
        else:
            print("1")
            print(address_port)
            adress2, port2 = address_port
            client2 = int(port2)

            if(client2 == client):  
                print("2")
                if( self.data == "makeroom"):
                    self.makeroom(address_port)
                elif(self.data == "getdir"):
                    self.getdir(address_port)
                elif(self.data == "deleteroom"):
                    self.deleteroom(address_port)
                elif(self.data == "bye"):
                    # text2 = ("Quit CRDS")
                    # text2 = text2.encode("utf-8")
                    # self.socket.sendto(text2, address_port)
                    self.mes = ""
                    print("Connection closed")
                    self.getmes()

                else:
                    text3 = ("command not find, please enter again")
                    text3 = text3.encode("utf-8")
                    self.socket.sendto(text3, address_port)
                    self.CRDS(address_port)
            else:
                 self.CRDS(address_port)
            
            

    def threads(self,address_port):
        # while True:
        
        # self.socket, client_address = self.socket.accept()
        print("Connection received from {}.".format(address_port))
        client_thread = threading.Thread(target=self.connect_CRDS(address_port), args=(address_port))
        client_thread.daemon = True
        client_thread.start()
        
                  

    def get_socket(self):
        try:
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

            ############################################################            
            # Bind to an address/port. In multicast, this is viewed as
            # a "filter" that deterimines what packets make it to the
            # UDP app.
            ############################################################            
            self.socket.bind(RX_BIND_ADDRESS_PORT)

            ############################################################
            # The multicast_request must contain a bytes object
            # consisting of 8 bytes. The first 4 bytes are the
            # multicast group address. The second 4 bytes are the
            # interface address to be used. An all zeros I/F address
            # means all network interfaces. They must be in network
            # byte order.
            ############################################################
            multicast_group_bytes = socket.inet_aton(MULTICAST_ADDRESS)
            # or
            # multicast_group_int = int(ipaddress.IPv4Address(MULTICAST_ADDRESS))
            # multicast_group_bytes = multicast_group_int.to_bytes(4, byteorder='big')
            # or
            # multicast_group_bytes = ipaddress.IPv4Address(MULTICAST_ADDRESS).packed
            print("Multicast Group: ", MULTICAST_ADDRESS)

            # Set up the interface to be used.
            multicast_iface_bytes = socket.inet_aton(RX_IFACE_ADDRESS)

            # Form the multicast request.
            multicast_request = multicast_group_bytes + multicast_iface_bytes
            print("multicast_request = ", multicast_request)

            # You can use struct.pack to create the request, but it is more complicated, e.g.,
            # 'struct.pack("<4sl", multicast_group_bytes,
            # int.from_bytes(multicast_iface_bytes, byteorder='little'))'
            # or 'struct.pack("<4sl", multicast_group_bytes, socket.INADDR_ANY)'

            # Issue the Multicast IP Add Membership request.
            print("Adding membership (address/interface): ", MULTICAST_ADDRESS,"/", RX_IFACE_ADDRESS)
            self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_request)

        except Exception as msg:
            print(msg)
            sys.exit(1)


    def makeroom(self,address_port):
        self.mes2 = "Please enter room name"
        self.socket.sendto(self.mes2.encode("utf-8"), address_port)
        self.name_byte, address_portc = self.socket.recvfrom(Server.RECV_SIZE)
        addressc, portc = address_portc
        adress,port = address_port
        if(portc == port):
            self.name = self.name_byte.decode('utf-8')
            print("Received: {} {}".format(self.name, address_port))
            while(self.name == ""):
                self.name_byte, address_port = self.socket.recvfrom(Server.RECV_SIZE)
                address, port = address_port
                self.name = self.name_byte.decode('utf-8')
                print("Received: {} {}".format(self.name, address_port))

            while(self.name in self.dir_list):
                mes7 = "The room name already exists, please change the name of the room"
                self.socket.sendto(mes7.encode("utf-8"), address_port)
                self.name_byte, address_port = self.socket.recvfrom(Server.RECV_SIZE)
                self.name = self.name_byte.decode('utf-8')
                print("Received: {} {}".format(self.name, address_port))
            print ("Room estabilshed\n Back to CRDS, Please enter your command")
            l = self.muticast_address.split('.')
            a= int(l[3])+1
            l[3] = str(a)
            stra = "."
            self.muticast_address = stra.join(l)
            self.port = 2000
            self.get_chatroom_socket()
            self.mes3 = "Room estabilshed\n Back to CRDS, Please enter your command"
            self.socket.sendto(self.mes3.encode("utf-8"), address_port)
            self.CRDS(address_port)
        else:
            self.makeroom(address_port)

    def get_chatroom_socket(self):
        try:
            
            self.muticast_address_port = (self.muticast_address,self.port)
            self.chat_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.chat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

            ############################################################            
            # Bind to an address/port. In multicast, this is viewed as
            # a "filter" that deterimines what packets make it to the
            # UDP app.
            ############################################################            
            self.chat_socket.bind(RX_BIND_ADDRESS_PORT)

            ############################################################
            # The multicast_request must contain a bytes object
            # consisting of 8 bytes. The first 4 bytes are the
            # multicast group address. The second 4 bytes are the
            # interface address to be used. An all zeros I/F address
            # means all network interfaces. They must be in network
            # byte order.
            ############################################################
            multicast_group_bytes = socket.inet_aton(self.muticast_address)
            # or
            # multicast_group_int = int(ipaddress.IPv4Address(MULTICAST_ADDRESS))
            # multicast_group_bytes = multicast_group_int.to_bytes(4, byteorder='big')
            # or
            # multicast_group_bytes = ipaddress.IPv4Address(MULTICAST_ADDRESS).packed
            print("Multicast Group: ", self.muticast_address)

            # Set up the interface to be used.
            multicast_iface_bytes = socket.inet_aton(RX_IFACE_ADDRESS)

            # Form the multicast request.
            multicast_request = multicast_group_bytes + multicast_iface_bytes
            print("multicast_request = ", multicast_request)

            # You can use struct.pack to create the request, but it is more complicated, e.g.,
            # 'struct.pack("<4sl", multicast_group_bytes,
            # int.from_bytes(multicast_iface_bytes, byteorder='little'))'
            # or 'struct.pack("<4sl", multicast_group_bytes, socket.INADDR_ANY)'

            # Issue the Multicast IP Add Membership request.
            print("Adding membership (address/interface): ", self.muticast_address,"/", RX_IFACE_ADDRESS)
            self.chat_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_request)
            self.dir_list[self.name] = [self.muticast_address, self.port,self.chat_socket]
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def getdir(self,address_port):
        print("getdir function")
        print(self.dir_list)
        mes4 = ""
        for i in self.dir_list.keys():
            mes4 = mes4 +i + " "+ str(self.dir_list[i][0])+ " "+str(self.dir_list[i][1]) +"\n"
        self.socket.sendto(mes4.encode("utf-8"), address_port)
        self.CRDS(address_port)
        print("dir sent\n Back to CRDS, Please enter your command")

    def deleteroom(self,address_port):
        self.mes5 = "Please enter room name"
        self.socket.sendto(self.mes5.encode("utf-8"), address_port)
        self.dname_byte, address_port = self.socket.recvfrom(Server.RECV_SIZE)
        address, port = address_port
        self.dname = self.dname_byte.decode('utf-8')
        print("Received: {} {}".format(self.dname, address_port))
        self.soket2 = self.dir_list[self.dname][2]
        self.soket2.close()
        del self.dir_list[self.dname]
        mes6 = "Room is delete\n Back to CRDS, Please enter your command"
        self.socket.sendto(mes6.encode("utf-8"), address_port)
        self.CRDS(address_port)

    def check_room(self):
        print("into check room")
    #     self.input, address_port = self.socket.recvfrom(Server.RECV_SIZE)
    #     address, port = address_port
    #     if(self.input in self.dir_list ):
    #         self.send_messages_forever()
            
    # def send_messages_forever(self):
        try:
            self.socketc = self.dir_list[self.mes][2]
            while True:   
                self.chat, address_port = self.socketc.recvfrom(Server.RECV_SIZE)
                self.chata = self.chat.decode('utf-8')
                chat_text = self.chata.split(':')
                if chat_text[1] == 'exit' :
                    self.getmes()
                else:
                    print("Received: {} {}".format(self.chat, address_port))
                    for i in self.client_list:
                        address = '192.168.2.12'
                        address_porta = (address,i)
                        chat_address_port = (self.dir_list[self.mes][0],self.dir_list[self.mes][1])
                        self.socketc.sendto(self.chat,address_porta)
                        
                ########################################################
                # Send the multicast packet
                
                # Sleep for a while, then send another.

        except Exception as msg:
            print(msg)
        except KeyboardInterrupt:
            print()
        finally:
            self.socket.close()
            sys.exit(1)

########################################################################
# Multicast Sender
########################################################################

class Client:

    HOSTNAME = socket.gethostname()

    TIMEOUT = 2
    RECV_SIZE = 1024
    
    MSG_ENCODING = "utf-8"
    MESSAGE =  HOSTNAME + " multicast beacon: "
    MESSAGE_ENCODED = MESSAGE.encode('utf-8')
    RECV_BUFFER_SIZE = 1024 # Used for recv.
    # Create a 1-byte maximum hop count byte used in the multicast
    # packets (i.e., TTL, time-to-live).
    TTL = 1 # Hops
    TTL_BYTE = TTL.to_bytes(1, byteorder='big')
    # Or: TTL_BYTE = struct.pack('B', TTL)
    # Or: TTL_BYTE = b'01'

    def __init__(self):
        self.connect_to_server()
        self.send_console_input_forever()
          
    def send_console_input_forever(self):
        while True:
            try:
                print("Command list: connect, name, chat")
                self.command = input("Command: ")
                if self.command != '':
                    self.get_cmd()        
            except (KeyboardInterrupt, EOFError):
                print()
                print("Closing client socket ...")
                self.socket.close()
                sys.exit(1)

    def get_cmd(self):
        if (self.command == "connect"):
            self.socket.sendto(self.command.encode(Server.MSG_ENCODING),MULTICAST_ADDRESS_PORT)
            self.communicate_server()
        elif (self.command == "chat"):
            #self.socket.sendto(self.command.encode(Server.MSG_ENCODING),MULTICAST_ADDRESS_PORT)
            self.chat()
        elif(self.command == "name"):
            self.name()

    def connect_to_server(self):
        self.create_send_socket()
  

    def create_send_socket(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            ############################################################
            # Set the TTL for multicast.

            self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, Client.TTL_BYTE)

            ############################################################
            # Bind to the interface that will carry the multicast
            # packets, or you can let the os decide, which is usually
            # ok for a laptop or simple desktop.

            # self.socket.bind((IFACE_ADDRESS, 30000))
            self.socket.bind((IFACE_ADDRESS, 0)) # Have the system pick a port number.

        except Exception as msg:
            print(msg)
            sys.exit(1)


    def chat(self):
        print("Please enter the chat room name")
        self.room_name = input("chat room name:")
        if(self.room_name in self.dir_list):
            print("Enter the chat room")
            self.socket.sendto(self.room_name.encode(Server.MSG_ENCODING),MULTICAST_ADDRESS_PORT)
            chat_address_port = ((self.dir_list[1]),int(self.dir_list[2]))
            receiver_thread = threading.Thread(target=self.receive_chat_messages)
            receiver_thread.start()
            while True:
                self.input = input()
                self.chat_text = self.chatname+":"+ self.input
                if(self.input == "exit"):
                    self.send_console_input_forever()


                # Send string objects over the connection. The string must
                # be encoded into bytes objects first.
                self.socket.sendto(self.chat_text.encode(Server.MSG_ENCODING),chat_address_port)

    def receive_chat_messages(self):
        while True:
                recvd_bytes = self.socket.recv(Client.RECV_BUFFER_SIZE)
                print(recvd_bytes.decode(Server.MSG_ENCODING))

    def communicate_server(self):

        try:
            num = 0;
            while True: 
                recvd_bytes = self.socket.recv(Client.RECV_BUFFER_SIZE)
                print("Received: ", recvd_bytes.decode(Server.MSG_ENCODING))
                if(num == 1):
                    self.dir_list = recvd_bytes.decode(Server.MSG_ENCODING)
                    # print(self.dir_list)
                    self.dir_list = self.dir_list.split(' ')                                   
                self.input_text = input("Input:")
                self.socket.sendto(self.input_text.encode(Server.MSG_ENCODING),MULTICAST_ADDRESS_PORT)
                if (self.input_text == "bye"):
                    print("Connection closed")
                    self.send_console_input_forever()
                if(self.input_text == "getdir"):
                    num = 1;
                

        except Exception as msg:
            print(msg)
            sys.exit(1)
        except Exception as msg:
            print(msg)
        except KeyboardInterrupt:
            print()
        finally:
            self.socket.close()
            sys.exit(1)
    def name(self):
        print("Please enter your chat name")
        self.chatname = input("Enter chat name:")
########################################################################
# Process command line arguments if run directly.

########################################################################

if __name__ == '__main__':
    roles = {'server': Server,'client': Client}
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--role',
                        choices=roles, 
                        help='server or client role',
                        required=True, type=str)

    args = parser.parse_args()
    roles[args.role]()

########################################################################











