
"""
    UDPServer.py creates a UDP socket that listens for UDP mesages to be send.
    First the client sends a request to connect (WRQ, opcode 2) and the server will
    respond with an inital ACK (opcode 4). The client then send a single DATA
    packets (opcode 3) and waits for an ACK from the server before sending the next
    DATA packet. If the client chooses to send a file then opcode 6 is used. This
    program deals with packet loss by never senting the next packet until an ACK is
    recieve for the previous one. If a packet is lost then the sender waiting for
    an ACK will timeout and resend the packet.
    """

import socket
from datetime import datetime
import sys
from random import randint

# for each sendto/recvfrom there will be 1/RANDRANGE chance of packet loss
RANDRANGE = 3   # 100/RANDRANGE packet loss percentage for each possible point of loss
isFile = False  # flag to handle file transfers
TIMEOUTTIME = 0.2   # timeout time for blocking send and recv

def makeDATApackets(msg):
    """Turns the msg into an list of formated DATA packets
        
        The source host sends numbered DATA packets to the destination host, all
        but the last contain a full-sized block of data (512 bytes).
        """
    packets = []    # list to be returned
    opcode = "3"    # opcode for DATA packets is 3
    c = 0           # count variable to help order multiple packets
    if isFile and msg[-6:-1] != "[y:n]":
        # add file and data opcode and count to begining of message if file
        msg = "6"+opcode+str(c)+msg
    else:
        msg = opcode + str(c) + msg     # add opcode and count to start of message
    # break message into multiple packets if the message is longer than 512 btyes
    while sys.getsizeof(msg) >= 512:
        packets.append(msg[:512])   # add message segment to return list
        c += 1 % 10     # incrament count variable while keeping it a single digit
        # add opcode and count to begining of packet
        msg = opcode + str(c) + msg[512:]
    packets.append(msg[:512])
    return packets

def sendmsg(msg, hostname, port):
    serverSocket.settimeout(TIMEOUTTIME)    # set timeout time
    connectAttempts = 0     # if cannot connect after 5 trys funciton will quit
    while connectAttempts < 5:  # initialize connection
        # The initiating host sends an WRQ (write request) packet to the server
        # containing the opcode (2 for WRQ) and message id (begining of message).
        if not randint(0,RANDRANGE) == 1:   # adding packet loss probability
            serverSocket.sendto(("2"+message[:474]).encode(), (hostname, port))
        else:
            print("packet loss line 51")
        if not randint(0,RANDRANGE) == 1:   # adding packet loss probability
            try:    # wait to recieve the response
                recievedMessage, serverAddress = serverSocket.recvfrom(512)
                if recievedMessage[0] == "4": # opcode for ACK packets is 4
                    # Sender responds to the first received ACK of a block with
                    # DATA of the next block.
                    break
            except socket.timeout:  # if not response occured within TIMEOUTTIME
                # If an ACK is not eventually received, a retransmit timer re-sends
                # WRQ packet.
                connectAttempts += 1    # keep track of failed attempts to connect
#                print(str(datetime.now()) + " timeout first while")
                pass
        else:
            print("packet loss line 56")
    if connectAttempts >= 5:    # if 5 attempts to connect failed
        print("Client not responsing")
        serverSocket.settimeout(None)  # socket is set to blocking mode
        return False    # exit funciton

    packets = makeDATApackets(msg)  # break message into a list of DATA packets
    for packet in packets:
        if not randint(0,RANDRANGE) == 1:   # adding packet loss probability
            # send first packet
            serverSocket.sendto(packet.encode(), (hostname, port))
        else:
            print("packet loss line 78")
        while True:     # try to recieve ACKs
            if not randint(0,RANDRANGE) == 1:   # adding packet loss probability
                try:    # wait to recieve ACK
                    recievedMessage, serverAddress = serverSocket.recvfrom(512)
                    if recievedMessage[0] == "4": # opcode for ACK packets is 4
                        # Sender responds to the first received ACK of a block with
                        # DATA of the next block.
                        break
                except socket.timeout:  # if no response occured within TIMEOUTTIME
                    # adding packet loss probability
                    if not randint(0,RANDRANGE) == 1:
                        # resend packet
                        serverSocket.sendto(packet.encode(), (hostname, port))
                    else:
                        print("packet loss line 93")
#                    print(str(datetime.now()) + " timeout 2nd while")
                    pass
            else:
                print("packet loss line 84")
    serverSocket.settimeout(None)   # socket is set to blocking mode
    return True     # successfully sent and exit

def fileoption(clientAddress):
    toremove = False
    for client in clients:  # for each client in chat group
        if client == clientAddress:     # don't send file to owner
            continue
        # attach destination address to message and send packet
        message="<"+clientAddress[0]+":"+str(clientAddress[1])+"> wants to send you a file. Press 'y' to except."
        if not sendmsg(message, client[0], client[1]):
            # if failed to send
            toremove = client   # we will remove client from chat group
    if toremove:    # if failed to send
        clients.remove(toremove)    # remove client from chat group
            
    while True:
        # recieve message and address from client with a buffer size of 512
        if not randint(0,RANDRANGE) == 1: # adding packet loss probability
            message, clientAddress = serverSocket.recvfrom(512)
            if clientAddress in clients:    # if in chat room
                if message[0] == "2":   # if we recieved a WRQ (opcode 2)
                    # Then server replies with ACK (opcode 4) and count
                    if not randint(0,RANDRANGE) == 1: # adding packet loss probab.
                        serverSocket.sendto(("40").encode(), clientAddress)
                    else:
                        print("packet loss line 124")
                    message = recvmsg(clientAddress)    # revieve message
                    return message[0] == "y"
        else:
            print("packet loss line 119")

def recvmsg(address):
    serverSocket.settimeout(TIMEOUTTIME)  # set timeout time
    # The destination host replies with numbered ACK packets for all DATA packets.
    c = 0           # count variable to help order multiple packets
    message = ""    # returning string that accumulates the message
    while True:
        if not randint(0,RANDRANGE) == 1:   # adding packet loss probability
            try:    # wait to recieve packet
                recievedMessage, clientAddress = serverSocket.recvfrom(512)
                if recievedMessage[0] == "6":   # opcode for a file
                    global isFile
                    isFile = True
                    recievedMessage = recievedMessage[1:]
                if recievedMessage[0] == "2":   # recieved another WRQ (opcode 2)
                    # Then server replies with an initial ACK (opcode 4)
                    if not randint(0,RANDRANGE) == 1: # packet loss probability
                        serverSocket.sendto(("40").encode(), clientAddress)
                    else:
                        print("packet loss line 148")
                # else if DATA packet (opcode 3) in the correct order
                # "3"+str(c) expected but check for "3"+str(c) incase ACK was lost
                elif recievedMessage[:2] == "3"+str(c) or recievedMessage[:2] == "3"+str(c-1):
                    if sys.getsizeof(recievedMessage) < 512:    # if last packet
                        message += recievedMessage[2:]  # accumulate message
                        # Receiver responds to each DATA with associated numbered
                        # ACK.
                        if not randint(0,RANDRANGE) == 1:
                            # adding packet loss probability
                            serverSocket.sendto(("4"+str(c)).encode(), clientAddress)
                        else:
                            print("packet loss line 160")
                        break
                    else:   # if not last packet
                        if recievedMessage[:2] == "3"+str(c):   # as expected
                            message += recievedMessage[2:]  # accumulate message
                            c = (c + 1) % 10
                        # Receiver responds to each DATA with associated numbered
                        # ACK.
                        if not randint(0,RANDRANGE) == 1:
                            # adding packet loss probability
                            serverSocket.sendto(("4"+str(c)).encode(), clientAddress)
                        else:
                            print("packet loss line 172")
            except socket.timeout:  # if not response occured within TIMEOUTTIME
#                print(str(datetime.now()) + " timeout in recvmsg()")
                if not randint(0,RANDRANGE) == 1: # adding packet loss probability
                    # resend ACK
                    serverSocket.sendto(("40").encode(), address)
                else:
                    print("packet loss line 179")
                pass
        else:
            print("packet loss line 140")
    serverSocket.settimeout(None)  # socket is set to blocking mode
    return message


serverPort = 12000      # the server port number
clients = []            # list of current clients

# create UDP socket using IPv4
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# assigns port number to the server's socket
serverSocket.bind(('', serverPort))

# display message letting us know that the bind was successful
print("The server is ready to receive.")

while True:
    # recieve message and address from client with a buffer size of 512
    if not randint(0,RANDRANGE) == 1: # adding packet loss probability
        message, clientAddress = serverSocket.recvfrom(512)
        # if client address is new and there is less than current 3 users
        if (clientAddress not in clients) and (len(clients) < 3):
            clients.append(clientAddress)   # then add them to the chat group
            print('<'+clientAddress[0]+":"+str(clientAddress[1])+'> '+" joined chat")
        if clientAddress in clients:    # if in chat room
            if message[0] == "2":   # if we recieved a WRQ (opcode 2)
                # Then server replies with ACK (opcode 4) and count
                if not randint(0,RANDRANGE) == 1: # adding packet loss probability
                    serverSocket.sendto(("40").encode(), clientAddress)
                else:
                    print("packet loss line 213")
                isFile = False
                recvmessage = recvmsg(clientAddress)    # revieve message
                if isFile:
                    if not fileoption(clientAddress):
                        continue
                    message = recvmessage
                else:
                    # add ID to begining of message
                    message='<'+clientAddress[0]+':'+str(clientAddress[1])+'> '+recvmessage
                toremove = None     # to know if message send was successful
                for client in clients:  # for each client in chat group
                    # attach destination address to message and send packet
                    if isFile and client == clientAddress:
                        continue
                    if not sendmsg(message, client[0], client[1]):
                        # if failed to send
                        toremove = client   # we will remove client from chat group
                if toremove:    # if failed to send
                    clients.remove(toremove)    # remove client from chat group
        else:   # someone's trying to join but the group is full
            print("chat room full")
    else:
        print("packet loss line 204")

serverSocket.close()    # close the close
