"""
    UDPClient.py creates a UDP socket that can send messages to the server and the
    sever will send that message to ever client in the chat group. The client can
    also send a file to every other user in the group if a user chooses to accept
    it. Please see UDPServer.py for infomation of the transfer protocol used.
    """

import socket
import sys
import select
from datetime import datetime
TIMEOUTTIME = 0.5           # timeout time for blocking send and recv
isFile = False              # flag to handle file transfers

def makeDATApackets(msg, file):
    """Turns the msg into an list of formated DATA packets
        
        The source host sends numbered DATA packets to the destination host, all
        but the last contain a full-sized block of data (512 bytes).
        """
    packets = []    # list to be returned
    opcode = "3"    # opcode for DATA packets is 3
    c = 0           # count variable to help order multiple packets
    if file:    # sending a file
        msg="6"+opcode+str(c)+msg   # add opcodes and count to begining of message
    else:
        msg = opcode+str(c)+msg     # add opcode and count to begining of message
    # break message into multiple packets if the message is longer than 512 btyes
    while sys.getsizeof(msg) >= 512:
        packets.append(msg[:512])   # add message segment to return list
        c = (c + 1) % 10    # increment single digit count variable
        # add opcode and count to begining of packet
        msg = opcode + str(c) + msg[512:]
    packets.append(msg[:512])
    return packets

def sendmsg(msg, hostname, port, file=False):
    while True:     # initialize connection
        # The initiating host sends an WRQ (write request) packet to the server
        # containing the opcode (2 for WRQ) and message id (begining of message).
        clientSocket.sendto(("2"+message[:474]).encode(), (hostname, port))
        try:    # wait to recieve the response
            recievedMessage, serverAddress = clientSocket.recvfrom(512)
            if recievedMessage[0] == "4": # opcode for ACK packets is 4
                # Sender responds to the first received ACK of a block with
                # DATA of the next block.
                break
        except socket.timeout:  # if not response occured within TIMEOUTTIME
            # If an ACK is not eventually received, a retransmit timer re-sends
            # WRQ packet.
#            print(str(datetime.now()) + " timeout first while")
            pass
    
    packets = makeDATApackets(msg, file)    # turn msg into list of DATA packets
    for packet in packets:
        while True:     # try to recieve ACKs
            # send first packet
            clientSocket.sendto(packet.encode(), (hostname, port))
            try:    # wait to recieve ACK
                recievedMessage, serverAddress = clientSocket.recvfrom(512)
                if recievedMessage[0] == "4": # opcode for ACK packets is 4
                    # Sender responds to the first received ACK of a block with
                    # DATA of the next block.
                    break
                if recievedMessage[0] == "2":
                    # final ACK was lost but server is sending message so the
                    # server did recieve the final data packet
                    break
            except socket.timeout:  # if not response occured within TIMEOUTTIME
                # If an ACK is not eventually received, a retransmit timer re-sends
                # DATA packet.
#                print(str(datetime.now()) + " timeout 2nd while")
                pass

def recvmsg(address):
    clientSocket.settimeout(TIMEOUTTIME)  # set timeout time
    # The destination host replies with numbered ACK packets for all DATA packets.
    c = 1           # count variable to help order multiple packets
    message = ""    # returning string that accumulates the message
    while True:
        try:    # wait to recieve packet
            recievedMessage, clientAddress = clientSocket.recvfrom(512)
            if recievedMessage[0] == "6":   # opcode for a file
                global isFile
                isFile = True
                recievedMessage = recievedMessage[1:]
            if recievedMessage[0] == "3":   # if recieving a DATA packet (opcode 3)
                if sys.getsizeof(recievedMessage) < 512:    # if last packet
                    message += recievedMessage[2:]  # accumulate message
                    # Receiver responds to each DATA with associated numbered ACK.
                    clientSocket.sendto(("4"+str(c)).encode(), clientAddress)
                    break
                else:   # if not last packet
                    message += recievedMessage[2:]  # accumulate message
                    # Receiver responds to each DATA with associated numbered ACK.
                    clientSocket.sendto(("4"+str(c)).encode(), clientAddress)
            c += 1  # increment the counter
        except socket.timeout:  # if not response occured within TIMEOUTTIME
#            print(str(datetime.now()) + " timeout in recvmsg()")
            pass
    return message


serverName = 'localhost'    # the IP address or the hostname of the server
serverPort = 12000          # the server port number

# create UDP socket using IPv4
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

clientSocket.settimeout(TIMEOUTTIME)      # set timeout time

print('Enter message to begin chatting. Use "transferfile <filename>" to trasfer a file\n')

while True:
    inputs = [sys.stdin, clientSocket]  # maintains a list of possible inputs
    # waits until an input is ready for reading
    read_sockets, write_socket, error_socket = select.select(inputs,[],[])
    # loop on the inputs read to be read
    for socks in read_sockets:
        if socks == clientSocket:   # if input is from the socket
            # recieve message and address from client with a buffer size of 512
            message, clientAddress = clientSocket.recvfrom(512)
            if message[0] == "2":   # if we recieved a WRQ (opcode 2)
                # Then replies with an initial ACK packet (opcode 4)
                clientSocket.sendto(("40").encode(), clientAddress)
                message = recvmsg(clientAddress)    # recieve message from server
                if isFile:
                    filename = raw_input("Enter name for file and it's path ")
                    with open(filename, "w") as f:
                        f.write(message)
                    isFile = False
                else:
                    sys.stdout.write(message)   # write message to commandline
                    sys.stdout.flush()
        else:   # if input is from commandline
            message = sys.stdin.readline()  # read the user's typed text
            if len(message) > 1:    # to only send messages with content
                if message[:12] == "transferfile":  # command to transfer file
                    try:
                        f = open(message[13:-1], 'r')     # open file to read
                    except:
                        print("file not found")
                        continue
                    else:
                        message = f.read()    # turn file into string
                        f.close()
                        sendmsg(message, serverName, serverPort, True)  # send file
                else:
                    sendmsg(message, serverName, serverPort)  # send the message

clientSocket.close()    # close the socket
