#Hengbo Huang / Yinwen Xu Lab 3 code

#file_download
#+service_discovery
#!/usr/bin/env python3

########################################################################
#
# Simple File Request/Download Protocol
#
########################################################################
#
# When the client connects to the server and wants to request a file
# download, it sends the following message: 1-byte GET command + 1-byte
# filename size field + requested filename, e.g., 

# ------------------------------------------------------------------
# | 1 byte GET command  | 1 byte filename size | ... file name ... |
# ------------------------------------------------------------------

# The server checks for the GET and then transmits the requested file.
# The file transfer data from the server is prepended by an 8 byte
# file size field as follows:

# -----------------------------------
# | 8 byte file size | ... file ... |
# -----------------------------------

# The server needs to have REMOTE_FILE_NAME defined as a text file
# that the client can request. The client will store the downloaded
# file using the filename LOCAL_FILE_NAME. This is so that you can run
# a server and client from the same directory without overwriting
# files.

########################################################################

import socket
import argparse
import time
import sys
import datetime
########################################################################

# Define all of the packet protocol field lengths.

CMD_FIELD_LEN            = 1 # 1 byte commands sent from the client.
FILENAME_SIZE_FIELD_LEN  = 1 # 1 byte file name size field.
FILESIZE_FIELD_LEN       = 8 # 8 byte file size field.
    
# Define a dictionary of commands. The actual command field value must
# be a 1-byte integer. For now, we only define the "GET" command,
# which tells the server to send a file.

CMD = {"scan" : 1 , 
       "get"  : 2,
       "list" : 3,
       "put"  : 4}

MSG_ENCODING = "utf-8"
SOCKET_TIMEOUT = 100

########################################################################
# recv_bytes frontend to recv
########################################################################

# Call recv to read bytecount_target bytes from the socket. Return a
# status (True or False) and the received butes (in the former case).
def recv_bytes(sock, bytecount_target):
    # Be sure to timeout the socket if we are given the wrong
    # information.
    sock.settimeout(SOCKET_TIMEOUT)
    try:
        byte_recv_count = 0 # total received bytes
        recv_bytes = b''    # complete received message
        while byte_recv_count < bytecount_target:
            # Ask the socket for the remaining byte count.
            new_bytes = sock.recv(bytecount_target-byte_recv_count)
            # If ever the other end closes on us before we are done,
            # give up and return a False status with zero bytes.
            if not new_bytes:
                return(False, b'')
            byte_recv_count += len(new_bytes)
            recv_bytes += new_bytes
        # Turn off the socket timeout if we finish correctly.
        sock.settimeout(None)            
        return (True, recv_bytes)
    # If the socket times out, something went wrong. Return a False
    # status.
    except socket.timeout:
        sock.settimeout(None)        
        print("recv_bytes: Recv socket timeout!")
        return (False, b'')

########################################################################
# SERVER
########################################################################

class Server:

    HOSTNAME = "0.0.0.0"

    PORT = 50000
    RECV_SIZE = 1024
    BACKLOG = 5

    FILE_NOT_FOUND_MSG = "Error: Requested file is not available!"

    # This is the file that the client will request using a GET.
    # REMOTE_FILE_NAME = "greek.txt"
    # REMOTE_FILE_NAME = "twochars.txt"
    # REMOTE_FILE_NAME = "ocanada_greek.txt"
    # REMOTE_FILE_NAME = "ocanada_english.txt"
    REMOTE_FILE_NAME = "Huang's file.txt"
    def __init__(self):
        self.create_listen_socket()
        self.process_connections_forever()

    def create_listen_socket(self):
        try:
            # Create the TCP server listen socket in the usual way.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((Server.HOSTNAME, Server.PORT))
            #self.socket.bind((Client.ADDRESS, Client.port))
            self.socket.listen(Server.BACKLOG)
            print("Listening on port {} ...".format(Server.PORT))
        except Exception as msg:

            print(msg)
            exit()

    def process_connections_forever(self):
        try:
            while True:
                self.connection_handler(self.socket.accept())
                 # Do a recvfrom in order to obtain the identity of the
                # sender of the incoming packet.
                #self.message_handler(self.socket.recvfrom(Server.RECV_SIZE))               
        except KeyboardInterrupt:
            print()
        #finally:
            #self.socket.close()

    def message_handler(self, client):
        # recvfrom returns the contents of the received segment and
        # the identity of the sender.
        msg_bytes, address_port = client
        msg = msg_bytes.decode(Server.MSG_ENCODING)
        print("-" * 72)
        print("Message received from {}.".format(address_port))
        # print("Received Message Bytes: ", msg_bytes)
        # print("Decoded Message: ", msg)
        # time.sleep(20) # for attacker.

        # Echo the received bytes back to the sender.
        self.socket.sendto(msg_bytes, address_port)
        print("Echoed Message: ", msg)
        # print("Encoded Echoed Message Bytes: ", msg_bytes)

    def connection_handler(self, client):
        connection, address = client
        print("-" * 72)
        print("Connection received from {}.".format(address))

        ################################################################
        # Process a connection and see if the client wants a file that
        # we have.
        
        # Read the command and see if it is a GET command.
        status, cmd_field = recv_bytes(connection, CMD_FIELD_LEN)
        # If the read fails, give up.
        #if not status:
            #print("not status, Closing connection ...")
           # connection.close()
           # return
        # Convert the command to our native byte order.
        if cmd_field != "":
            cmd = int.from_bytes(cmd_field, byteorder='big')
            # Give up if we don't get a GET command.
            if cmd != CMD["get"]:
                print("get command not received. Closing connection ...")
                connection.close()
                return

            # GET command is good. Read the filename size (bytes).
            status, filename_size_field = recv_bytes(connection, FILENAME_SIZE_FIELD_LEN)
            if not status:
                print("not status2, Closing connection ...")            
                connection.close()
                return
            filename_size_bytes = int.from_bytes(filename_size_field, byteorder='big')
            if not filename_size_bytes:
                print("Connection is closed!")
                connection.close()
                return
            
            print('Filename size (bytes) = ', filename_size_bytes)

            # Now read and decode the requested filename.
            status, filename_bytes = recv_bytes(connection, filename_size_bytes)
            if not status:
                print("not status3, Closing connection ...")            
                connection.close()
                return
            if not filename_bytes:
                print("Connection is closed!")
                connection.close()
                return

            filename = filename_bytes.decode(MSG_ENCODING)
            print('Requested filename = ', filename)

            ################################################################
            # See if we can open the requested file. If so, send it.
            
            # If we can't find the requested file, shutdown the connection
            # and wait for someone else.
            try:
                file = open(filename, 'r').read()
            except FileNotFoundError:
                print(Server.FILE_NOT_FOUND_MSG)
                connection.close()                   
                return

            # Encode the file contents into bytes, record its size and
            # generate the file size field used for transmission.
            file_bytes = file.encode(MSG_ENCODING)
            file_size_bytes = len(file_bytes)
            file_size_field = file_size_bytes.to_bytes(FILESIZE_FIELD_LEN, byteorder='big')

            # Create the packet to be sent with the header field.
            pkt = file_size_field + file_bytes
            
            try:
                # Send the packet to the connected client.
                connection.sendall(pkt)
                print("Sending file: ", filename)
                print("file size field: ", file_size_field.hex(), "\n")
                # time.sleep(20)
            except socket.error:
                # If the client has closed the connection, close the
                # socket on this end.
                print("Closing client connection ...")
                connection.close()
                return
            finally:
                #connection.close()
                return

########################################################################
# CLIENT
########################################################################

class Client:

    #RECV_SIZE = 10

    # Define the local file name where the downloaded file will be
    # saved.
    DOWNLOADED_FILE_NAME = "filedownload.txt"
    RECV_SIZE = 1024
    MSG_ENCODING = "utf-8"    

    ADDRESS = "255.255.255.255"
    # BROADCAST_ADDRESS = "192.168.1.255"    
    port = 30000
    ADDRESS_PORT = (ADDRESS, port)

    SCAN_CYCLES = 3
    SCAN_TIMEOUT = 2

    SCAN_CMD = "SCAN"
    SCAN_CMD_ENCODED = SCAN_CMD.encode(MSG_ENCODING)
    command = ""
    TRANS_LIST = []
    def __init__(self):
        
        self.send_console_input_forever()
        
    def get_console_input(self):
        # In this version we keep prompting the user until a non-blank
        # line is entered.
        while True:
            self.command = input("Command: ")
            #if self.command != '':
                 #self.input_text_encoded = self.input_text.encode(Server.MSG_ENCODING)
                 #break
            
    def send_console_input_forever(self):
        while True:
            try:
                print("Command list: get, scan, connect, llist, rlist, put, bye")
                self.command = input("Command: ")
                if self.command != '':
                    self.get_cmd()

        
            except (KeyboardInterrupt, EOFError):
                print()
                print("Closing client socket ...")
                self.socket.close()
                sys.exit(1)            
    def get_socket(self):
        try:
            # Service discovery done using UDP packets.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        except Exception as msg:
            print(msg)
            exit()
        #try:
        #    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #except Exception as msg:
        #    print(msg)
        #    exit()
    
    def get_soket_broadcasts(self):
        try:
            # Service discovery done using UDP packets.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Arrange to send a broadcast service discovery packet.
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            # Set the socket for a socket.timeout if a scanning recv
            # fails.
            self.socket.settimeout(Client.SCAN_TIMEOUT);
        except Exception as msg:
            print(msg)
            sys.exit(1)       

    def connect_to_server(self):
        try:
            #self.socket.connect((Server.HOSTNAME, Server.PORT))
            if(self.address == ""):
                print("Please enter ip adress and port number")
                self.address = str(input("IP address: "))
                self.port = int(input("Port number: "))
                self.connect_to_server()
            #elif (self.address == "255.255.255.255" ):
                #self.get_soket_broadcasts()
                #self.socket.connect((self.address, self.port))
            else:
                self.get_socket()
                self.socket.connect((self.address, self.port))
            print("Connected to server",self.address,"on port",self.port )
        except Exception as msg:
            print(msg)
            exit()
    
    def get_cmd(self):
        if self.command == "get":
            self.get_file()
           # print("Connected to server",self.address,"on port",self.port)
            self.connect_to_server()
        elif self.command == "scan":
            self.get_soket_broadcasts()
            self.scan_for_service()
        elif self.command == "connect":
            print("Please enter IP address and Port number")
            self.address = str(input("IP address: "))
            self.port = int(input("Port number: "))
            self.address_port = (self.address, self.port)
            self.connect_to_server()
        elif self.command == "llist":
            self.get_local_list()
        elif self.command == "bye":
            self.socket.close()
            print(" Close the current  server connection.")
        elif self.command == "put":
            self.put_file()
            self.connect_to_server()
        elif self.command == "rlist":
            self.get_remote_list()
            self.connect_to_server()
        else:
            print ("Unknown command, please enter again")
            self.send_console_input_forever()



            

    def get_file(self):

        ################################################################
        # Generate a file transfer request to the server
        
        # Create the packet cmd field.
        cmd_field = CMD["get"].to_bytes(CMD_FIELD_LEN, byteorder='big')

        # Create the packet filename field.
        #filename_field_bytes = Server.REMOTE_FILE_NAME.encode(MSG_ENCODING)
        self.filename = input("Filename:")
        filename_field_bytes = self.filename.encode(MSG_ENCODING)
        # Create the packet filename size field.
        filename_size_field = len(filename_field_bytes).to_bytes(FILENAME_SIZE_FIELD_LEN, byteorder='big')

        # Create the packet.
        print("CMD field: ", cmd_field.hex())
        print("Filename_size_field: ", filename_size_field.hex())
        print("Filename field: ", filename_field_bytes.hex())
        
        pkt = cmd_field + filename_size_field + filename_field_bytes

        # Send the request packet to the server.
        self.socket.sendall(pkt)
        print("Sending to {} ...".format(self.address_port))
        #self.socket.sendto(pkt, self.address_port)
        ################################################################
        # Process the file transfer repsonse from the server
        
        # Read the file size field returned by the server.
        status, file_size_bytes = recv_bytes(self.socket, FILESIZE_FIELD_LEN)
        if not status:
            print("Closing connection ...")            
            self.socket.close()
            return

        print("File size bytes = ", file_size_bytes.hex())
        if len(file_size_bytes) == 0:
            self.socket.close()
            return

        # Make sure that you interpret it in host byte order.
        file_size = int.from_bytes(file_size_bytes, byteorder='big')
        print("File size = ", file_size)

        # self.socket.settimeout(4)                                  
        status, recvd_bytes_total = recv_bytes(self.socket, file_size)
        if not status:
            print("Closing connection ...")            
            self.socket.close()
            return
        # print("recvd_bytes_total = ", recvd_bytes_total)
        # Receive the file itself.
        try:
            # Create a file using the received filename and store the
            # data.
            print("Received {} bytes. Creating file: {}" \
                  .format(len(recvd_bytes_total), self.filename))

            with open(self.filename, 'w') as f:
                recvd_file = recvd_bytes_total.decode(MSG_ENCODING)
                f.write(recvd_file)
                self.TRANS_LIST.append("get " + self.filename)
            print(recvd_file)
        except KeyboardInterrupt:
            print()
            exit(1)

    def scan_for_service(self):
        # Collect our scan results in a list.
        scan_results = []

        # Repeat the scan procedure a preset number of times.
        for i in range(Client.SCAN_CYCLES):

            # Send a service discovery broadcast.
            print("Sending broadcast scan {}".format(i))            
            self.socket.sendto(Client.SCAN_CMD_ENCODED, Client.ADDRESS_PORT)
        
            while True:
                # Listen for service responses. So long as we keep
                # receiving responses, keep going. Timeout if none are
                # received and terminate the listening for this scan
                # cycle.
                try:
                    recvd_bytes, address = self.socket.recvfrom(Client.RECV_SIZE)
                    recvd_msg = recvd_bytes.decode(Client.MSG_ENCODING)

                    # Record only unique services that are found.
                    if (recvd_msg, address) not in scan_results:
                        scan_results.append((recvd_msg, address))
                        continue
                # If we timeout listening for a new response, we are
                # finished.
                except socket.timeout:
                    break

        # Output all of our scan results, if any.
        if scan_results:
            for result in scan_results:
                print(result)
        else:
            print("No services found.")

    def get_local_list(self):
        print( "Local List :")
        for i in self.TRANS_LIST :
            print(i)

    def get_remote_list(self):
        cmd_field = CMD["put"].to_bytes(CMD_FIELD_LEN, byteorder='big')
        try:
            # sendto takes the bytes to be sent and the identity of
            # the destination.
            self.socket.sendto(cmd_field, self.address_port)
            # print("Sent Message: ", self.input_text)
            # print("Sent Message Bytes: ", self.input_text_encoded)
        except Exception as msg:
            print(msg)
            sys.exit(1)
        self.remote_list,address = self.socket.recvfrom(Client.RECV_SIZE)
        print("Received Message: ", self.remote_list.decode(MSG_ENCODING))

    def put_file(self):
        cmd_field = CMD["put"].to_bytes(CMD_FIELD_LEN, byteorder='big')
        self.filename = input("Filename:")
        
        try:
            file = open(self.filename, 'r').read()
        except FileNotFoundError:
            print(Server.FILE_NOT_FOUND_MSG)
            self.socket.close()                
            return
        file_bytes = file.encode(MSG_ENCODING)
        file_size_bytes = len(file_bytes)
        file_size_field = file_size_bytes.to_bytes(FILESIZE_FIELD_LEN, byteorder='big')
        print("CMD field: ", cmd_field.hex())
        print("Filename_size_field: ", file_size_field.hex())
        print("Filename field: ", file_bytes.hex())
        pkt = cmd_field + file_size_field + file_bytes
        try:
            # Send the packet to the connected client.
            self.socket.sendall(pkt)
            print("Sending file: ", self.filename)
            print("file size field: ", file_size_field.hex(), "\n")
            self.TRANS_LIST.append("put " + self.filename)
            # time.sleep(20)
        except socket.error:
            # If the client has closed the connection, close the
            # socket on this end.
            print("Closing client connection ...")
            self.socket.close()
            return
        finally:
            #self.socket.close()
            return
########################################################################

if __name__ == '__main__':
    roles = {'client': Client,'server': Server}
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--role',
                        choices=roles, 
                        help='server or client role',
                        required=True, type=str)

    args = parser.parse_args()
    roles[args.role]()

########################################################################











