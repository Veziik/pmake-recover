#! /usr/bin/env python3
import socket
import os
import sys
import threading 
import subprocess

##################### Define system vars for run #####################
HOST = '127.0.0.1'
PORT = 50007


def handleConnection(connection,address):
	print('connection accepted')

def loop():
	clientThreads = set()
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
		serverSocket.bind((HOST, PORT))
		serverSocket.listen(1)
		while True:
			print('listening...')
			clientConnection , clientAddress = serverSocket.accept()
			clientThread = threading.Thread( target=handleConnection , args=(clientConnection,clientAddress))
			clientThreads.add(clientThread)
			clientThread.start()



def main():
	try:
		loop()
	except KeyboardInterrupt as e:
		print('exiting server')

if __name__ == '__main__':
	main()