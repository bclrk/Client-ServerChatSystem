# Client-Server Chat System

A chat program under the client-server architecture for real-time communication between 2 or 3 users. In case of 3 users, messages generated by one user will reach the other two (e.g., like a conference). The chat program allows a user to type messages, which will be conveyed and displayed to the other end(s). Note that under the client-server architecture, clients cannot directly communicate with each other and must communicate through a server. The user interface is text-based through the command line terminal.

This program only uses UDP sockets and no TCP sockets. This means that it implements reliability (of the messages) on top of UDP, within the program, without using TCP. The program will ensure packets are in order.

The program also implements a feature for the users to be able to exchange files. That is, in a two-user session chat between machines A and B, the user at machine A can upload a file to machine B. The machine B’s user will choose  where the incoming file should be placed, and using what name. The program works for both text files as well as binary files.
