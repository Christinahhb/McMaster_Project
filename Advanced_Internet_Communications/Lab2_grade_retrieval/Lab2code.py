#!/usr/bin/python3

"""
Echo Client and Server Classes

T. D. Todd
McMaster University

to create a Client: "python EchoClientServer.py -r client" 
to create a Server: "python EchoClientServer.py -r server" 

or you can import the module into another file, e.g., 
import EchoClientServer
e.g., then do EchoClientserver.Server()

"""

########################################################################

import socket
import argparse
import sys
from cryptography.fernet import Fernet
import struct
import csv
########################################################################
# Echo Server class
########################################################################

class Server:

    # Set the server hostname used to define the server socket address
    # binding. Note that "0.0.0.0" or "" serves as INADDR_ANY. i.e.,
    # bind to all local network interfaces.
    #HOSTNAME = "0.0.0.0"      # All interfaces.
    # HOSTNAME = "192.168.1.22" # single interface
    # HOSTNAME = "hornet"       # valid hostname (mapped to address/IF)
    HOSTNAME = "localhost"    # local host (mapped to local address/IF)
    # HOSTNAME = "127.0.0.1"    # same as localhost
    PORT = 50000
    # Server port to bind the listen socket.
    
    RECV_BUFFER_SIZE_for_id = 4
    RECV_BUFFER_SIZE_for_command = 1024 # Used for recv.
    
    MAX_CONNECTION_BACKLOG = 10

    # We are sending text strings and the encoding to bytes must be
    # specified.
    # MSG_ENCODING = "ascii" # ASCII text encoding.
    MSG_ENCODING = "utf-8" # Unicode text encoding.

    # Create server socket address. It is a tuple containing
    # address/hostname and port.
    SOCKET_ADDRESS = (HOSTNAME, PORT)

    def __init__(self):
        self.create_listen_socket()
        self.student_grades_database = "course_grades_2023.csv"
        self.import_student_grades_database()
        self.process_connections_forever()


    
    def import_student_grades_database(self):
        """Read in the student database, clean whitespace from each record,
        and parse them .

        """
        # Read in the employee database and clean whitespace from each
        # record.
        self.read_and_clean_database_records()

        # Read each line and parse the student name,id_number, Name, Encryption Key,
        #Marks of Lab 1,Lab 2,Lab 3,Lab 4,Midterm,Exam 1,Exam 2,Exam 3,Exam 4
        self.parse_student_records()   
    


    def read_and_clean_database_records(self):
        """Read a list of people from a database file and add them as
        employees to the company.

        Open the file and read in the lines, stripping off end-of-line
        characters. Ignore blank lines.

        """
        try:
            file = open(self.student_grades_database, "r")
            records = file.readlines()
            print("This is the data I read from CSV \n")
            for line in records:
                print(line)
            records.pop(0)

        except FileNotFoundError:
            print("Creating database: {}". format(self.student_grades_database))
            file = open(self.student_grades_database, "w+")

        # Read and process all non-blank lines in the file. The
        # following uses two list comprehensions.
        self.cleaned_records = [clean_line for clean_line in
                                [line.strip() for line in records]
                                if clean_line != '']

        #print(self.cleaned_records)
        file.close()
         
        # Or (using a generator):
        # file_lines = [line for line in
        #               (line.strip() for line in file.readlines())
        #               if line != '']
        # Or (requires to line.strip()s:
        # file_lines = [line.strip() for line in file.readlines() if
        # line.strip() != '']
        # print(file_lines)

     #GMA, GL1A, GL2A, GL3A, GL4A, GEA and GG GMA/GEA are “get midterm/exam average” and the others are “get lab average” commands
    def parse_student_records(self):
        """Split each line into Name,ID Number,Key,Lab 1,Lab 2,Lab 3,Lab 4,Midterm,Exam 1,Exam 2,Exam 3,Exam 4

        self.employee_list is a twelve-tuple containing these
        values. Convert the id number and each grade into an int.

        """
        try:
            self.student_grade_list = [
                (s[0].strip(), int(s[1].strip()), s[2].strip(), int(s[3].strip()), int(s[4].strip()), int(s[5].strip()),
                int(s[6].strip()), int(s[7].strip()),int(s[8].strip()), int(s[9].strip()),
                int(s[10].strip()),int(s[11].strip()) ) for s in
                [s.split(',') for s in self.cleaned_records]]
            
            self.ID_list = []
            self.GL1_list = []
            self.GL2_list = []
            self.GL3_list = []
            self.GL4_list = []
            self.GM_list = []
            self.GE1_list = []
            self.GE2_list = []
            self.GE3_list = []
            self.GE4_list = []

            self.dict_id_key = {}

            for i in self.student_grade_list:
                self.ID_list.append(i[1])
                self.GL1_list.append(i[3])
                self.GL2_list.append(i[4])
                self.GL3_list.append(i[5])
                self.GL4_list.append(i[6])
                self.GM_list.append(i[7])
                self.GE1_list.append(i[8])
                self.GE2_list.append(i[9])
                self.GE3_list.append(i[10])
                self.GE4_list.append(i[11])
                key = i[1]                              #Student ID
                value = i[2]                            #encryption key
                self.dict_id_key.update({key:value})    #update the dictionary for student ID and encryption key

            self.GL1A = self.get_average(self.GL1_list)
            self.GL2A = self.get_average(self.GL2_list)
            self.GL3A = self.get_average(self.GL3_list)
            self.GL4A = self.get_average(self.GL4_list)
            self.GMA = self.get_average(self.GM_list)
            self.GE1A = self.get_average(self.GE1_list)
            self.GE2A = self.get_average(self.GE2_list)
            self.GE3A = self.get_average(self.GE3_list)
            self.GE4A = self.get_average(self.GE4_list)

            #print(self.student_grade_list)
            #print(self.dict_id_key)
   

        except Exception as e:
            print("Error: Invalid people name input file.")
            print(str(e))
            exit()

   
    def get_average(*args):
        total_sum = 0
        total_count = 0
        for lst in args:
            if isinstance(lst, list):
                total_sum += sum(lst)
                total_count += len(lst)
        
        if total_count == 0:
            return 0
        else:
            return total_sum / total_count
                


    def create_listen_socket(self):
        try:
            # Create an IPv4 TCP socket.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Set socket layer socket options. This one allows us to
            # reuse the socket without waiting for any timeouts.
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind socket to socket address, i.e., IP address and port.
            self.socket.bind(Server.SOCKET_ADDRESS)

            # Set socket to listen state.
            self.socket.listen(Server.MAX_CONNECTION_BACKLOG)
            print("Listening on port {} ...".format(Server.PORT))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def process_connections_forever(self):
        try:
            while True:
                # Block while waiting for accepting incoming TCP
                # connections. When one is accepted, pass the new
                # (cloned) socket info to the connection handler
                # function. Accept returns a tuple consisting of a
                # connection reference and the remote socket address.
                self.connection_handler(self.socket.accept())
        except Exception as msg:
            print(msg)
        except KeyboardInterrupt:
            print()
        finally:
            # If something bad happens, make sure that we close the
            # socket.
            self.socket.close()
            sys.exit(1)

    def connection_handler(self, client):
        # Unpack the client socket address tuple.
        connection, address_port = client
        print("-" * 72)
        print("Connection received from {}.".format(address_port))
        # Output the socket address.
        print(client)

        while True:
            try:
                # Receive bytes over the TCP connection. This will block
                # until "at least 1 byte or more" is available.
                recvd_bytes = connection.recv(Server.RECV_BUFFER_SIZE_for_id)
                recvd_bytes2 = connection.recv(Server.RECV_BUFFER_SIZE_for_command)
            
                # If recv returns with zero bytes, the other end of the
                # TCP connection has closed (The other end is probably in
                # FIN WAIT 2 and we are in CLOSE WAIT.). If so, close the
                # server end of the connection and get the next client
                # connection.
                if len(recvd_bytes) == 0 & len(recvd_bytes2) ==0:
                    print("Closing client connection ... ")
                    connection.close()
                    break
                
                # Decode the received bytes back into strings. Then output
                # them.
                try:
                    recvd_id = struct.unpack('!i', recvd_bytes)[0]
                except struct.error as e:
                    print(f"struct error: {e}")
                    recvd_id = None

                recvd_str = recvd_bytes2.decode(Server.MSG_ENCODING)
                print("Received_id:", recvd_id)
                if recvd_id in self.ID_list:
                    print("User found.")
                else:
                    print("User not found.")
                    print("Closing client connection ... ")
                    connection.close()
                    break

                print("Received_command:", recvd_str)   
                #print("see here before encryption")
                
                # Send the received bytes back to the client. We are
                # sending back the raw data.

                #GMA, GL1A, GL2A, GL3A, GL4A, GEA and GG GMA/GEA are “get midterm/exam average” and the others are “get lab average” commands
                if recvd_id in self.dict_id_key:
                    encryption_key = self.dict_id_key[recvd_id]
                    # print("see here after key")
                    # rest of your code that uses encryption_key
                else:
                    print("error occurs for dict_id_key")
                    # handle the case where recvd_id is not found in dict_id_key
 
                
                encryption_key_bytes = encryption_key.encode(Server.MSG_ENCODING)
                fernet = Fernet(encryption_key_bytes)
                # print("see here")

                if recvd_str == 'GL1A' :
                    message = "The average grade of Lab 1  is :" + str(self.GL1A) + "\n"
                    message_bytes = message.encode(Server.MSG_ENCODING)
                    connection.sendall(fernet.encrypt(message_bytes))
                    print("Already sent the average grade of Lab 1.")

                elif recvd_str == 'GL2A' :
                    message = "The average grade of Lab 2  is :" + str(self.GL2A) + "\n"
                    message_bytes = message.encode(Server.MSG_ENCODING)
                    connection.sendall(fernet.encrypt(message_bytes))
                    print("Already sent the average grade of Lab 2.")

                elif recvd_str == 'GL3A' :
                    message = "The average grade of Lab 3  is :" + str(self.GL3A) + "\n"
                    message_bytes = message.encode(Server.MSG_ENCODING)
                    connection.sendall(fernet.encrypt(message_bytes))
                    print("Already sent the average grade of Lab 3.")

                elif recvd_str == 'GL4A' :
                    message = "The average grade of Lab 4  is :" + str(self.GL4A) + "\n"
                    message_bytes = message.encode(Server.MSG_ENCODING)
                    connection.sendall(fernet.encrypt(message_bytes))
                    print("Already sent the average grade of Lab 4.")

                elif recvd_str == 'GMA' :
                    message = "The average grade of midterm exam is :" + str(self.GMA) + "\n"
                    message_bytes = message.encode(Server.MSG_ENCODING)
                    connection.sendall(fernet.encrypt(message_bytes))
                    print("Already sent the average grade of midterm.")

                elif recvd_str == 'GEA' :
                    message = "The average grade of Exam 1  is : " + str(self.GE1A) + "\n" \
                              "The average grade of Exam 2  is : " + str(self.GE2A) + "\n" \
                              "The average grade of Exam 3  is : " + str(self.GE3A) + "\n" \
                              "The average grade of Exam 4  is : " + str(self.GE4A) + "\n" 
                    message_bytes = message.encode(Server.MSG_ENCODING)
                    connection.sendall(fernet.encrypt(message_bytes))
                    print("Already sent the average grade of 4 exams.")

                elif recvd_str == 'GG' :
                    index = 0
                    for i in range(len(self.ID_list)):
                        if self.ID_list[i] == recvd_id:
                            index = i
                
                    message = "Your grade of Lab 1  is :" + str(self.student_grade_list[index][3]) +"\n" \
                              "Your grade of Lab 2  is :" + str(self.student_grade_list[index][4]) +"\n" \
                              "Your grade of Lab 3  is :" + str(self.student_grade_list[index][5]) +"\n" \
                              "Your grade of Lab 4  is :" + str(self.student_grade_list[index][6]) +"\n" \
                              "Your grade of midterm  is :" + str(self.student_grade_list[index][7]) +"\n" \
                              "Your grade of exam 1  is :" + str(self.student_grade_list[index][8]) +"\n" \
                              "Your grade of exam 2  is :" + str(self.student_grade_list[index][9]) +"\n" \
                              "Your grade of exam 3  is :" + str(self.student_grade_list[index][10]) +"\n" \
                              "Your grade of exam 4  is :" + str(self.student_grade_list[index][11]) +"\n"
                    message_bytes = message.encode(Server.MSG_ENCODING)
                    connection.sendall(fernet.encrypt(message_bytes))
                    print("Already sent the all grades of your labs and exams.")
                
                # print("see after if")

            except KeyboardInterrupt:
                print()
                print("Closing client connection ... ")
                connection.close()
                break


########################################################################
# Echo Client class
########################################################################

class Client:
    command = "";
    student_id = "";
    encryption_key = "none";
    # Set the server to connect to. If the server and client are running
    # on the same machine, we can use the current hostname.
    # SERVER_HOSTNAME = socket.gethostname()
    # SERVER_HOSTNAME = "192.168.1.22"
    SERVER_HOSTNAME = "localhost"
    
    # Try connecting to the compeng4dn4 echo server. You need to change
    # the destination port to 50007 in the connect function below.
    # SERVER_HOSTNAME = 'compeng4dn4.mooo.com'

    # RECV_BUFFER_SIZE = 5 # Used for recv.    
    RECV_BUFFER_SIZE = 1024 # Used for recv.
    
    def __init__(self):
        while(1):
            print(" Please enter student ID and command")
            print(" user commands list : GMA, GL1A, GL2A, GL3A, GL4A, GEA, GG")

            self.get_console_input(); 
            if(self.command != ""):
                self.get_socket()
                self.connect_to_server()
                self.send_console_input_forever()

  

    def get_socket(self):
        try:
            # Create an IPv4 TCP socket.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Allow us to bind to the same port right away.            
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Bind the client socket to a particular address/port.
            # self.socket.bind((Server.HOSTNAME, 40000))
                
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connect_to_server(self):
        try:
            # Connect to the server using its socket address tuple.
            self.socket.connect((Client.SERVER_HOSTNAME, Server.PORT))
            print("Connected to \"{}\" on port {}".format(Client.SERVER_HOSTNAME, Server.PORT))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def get_console_input(self):
        # In this version we keep prompting the user until a non-blank
        # line is entered, i.e., ignore blank lines.
        
        Command_list = ["GMA", "GL1A", "GL2A", "GL3A", "GL4A", "GEA", "GG"]
        while True:
            self.student_id = int(input("Student ID: "))
            self.command = input("Command: ")
            if self.command != "":
                print("Command entered:",self.command)
                if (self.command == "GMA" ):
                    print("Fetching Midterm average")
                elif(self.command == "GEA"):
                    print("Fetching Exam average")
                elif(self.command == "GL1A"):
                    print("Fetching Lab1 average")
                elif(self.command == "GL2A"):
                    print("Fetching Lab2 average")
                elif(self.command == "GL3A"):
                    print("Fetching Lab3 average")
                elif(self.command == "GL4A"):
                    print("Fetching Lab4 average")
                elif(self.command == "GG"):
                    print("Fetching Grade of student", self.student_id)
                else:
                    while self.command not in Command_list:
                        print("Commands not found.")
                        self.command = input("Reenter a Valid Command: ")
                break
                    
    
    def send_console_input_forever(self):
        
            
        #self.get_console_input()
        self.connection_send()
        self.connection_receive()
        #if (KeyboardInterrupt, EOFError):
            #print()
            #print("Closing server connection2 ...")
            # If we get and error or keyboard interrupt, make sure
            # that we close the socket.
            #self.socket.close()
            #sys.exit(1)
                
    def connection_send(self):
        try:
            # Send string objects over the connection. The string must
            # be encoded into bytes objects first.
            id_pack = struct.pack('!i',self.student_id)
            self.socket.sendall(id_pack)
            self.socket.sendall(self.command.encode(Server.MSG_ENCODING))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connection_receive(self):
        try:
            # Receive and print out text. The received bytes objects
            # must be decoded into string objects.
            recvd_bytes = "";
            recvd_bytes = self.socket.recv(Client.RECV_BUFFER_SIZE)
            #encryption_key = "M7E8erO15CIh902P8DQsHxKbOADTgEPGHdiY0MplTuY="
            self.read_csv()
            self.find_key()
            encryption_key_bytes = self.encryption_key.encode(Server.MSG_ENCODING)
            fernet = Fernet(encryption_key_bytes)
            recvd_bytes_decryption = fernet.decrypt(recvd_bytes)
            # recv will block if nothing is available. If we receive
            # zero bytes, the connection has been closed from the
            # other end. In that case, close the connection on this
            # end and exit.

            
            if recvd_bytes == "close" :
                print("Received: ", recvd_bytes.decode(Server.MSG_ENCODING))
                print("Closing server connection ... ")
                self.socket.close()
                sys.exit(1)                
            else:
                print("Received: ", recvd_bytes_decryption.decode(Server.MSG_ENCODING))
                print("Closing server connection ... \n\n")
                #self.socket.close()
                self.command = ""
                

        except Exception as msg:
            print(msg)
            sys.exit(1)

    def read_csv(self):
        self.student_list = list(csv.reader(open('decode_key.csv')))
    def find_key(self):
        for i in range(21):
            if( str(self.student_id) == str(self.student_list[i][1]) ):
                self.encryption_key = self.student_list[i][2]
                
########################################################################
# Process command line arguments if this module is run directly.
########################################################################

# When the python interpreter runs this module directly (rather than
# importing it into another file) it sets the __name__ variable to a
# value of "__main__". If this file is imported from another module,
# then __name__ will be set to that module's name.

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






