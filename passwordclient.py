#! /usr/bin/env python3
import socket
import sys


##################### Define system vars for run #####################
HOST = '127.0.0.1'
PORT = 50007


def parse():

	if len(sys.argv) < 4:
		print("""\nusage: """ +sys.argv[0] + """ <key> <save location> <length>
			-s: show recovered password in shell, off be default
			-e: recover from encrypted file, on by default
			-eN: recover from non-ecrypted padded file, off by defaut""")
		sys.exit(0)

	arguments = dict()

	arguments['writePath'] = sys.argv[2] #+ '.card'
	arguments['trashLength'] = seedFrontTrashlength()
	arguments['length']= int(sys.argv[3])
	arguments['encrypted']= True
	arguments['key'] = hashlib.sha256(sys.argv[1].encode('ascii')).hexdigest()[0:32]
	arguments['showPass'] = False
	
	
	
	for i in range(0, len(sys.argv)):
		if sys.argv[i] == '-eN':
			arguments['encrypted'] = False
		if sys.argv[i] == '-e':
			arguments['encrypted'] = True
		if sys.argv[i] == '-s':
			arguments['showPass'] = True

	return arguments

		
def sendRequest(arguments, serverConnection, ServerAddress):
	flags = 0b00

	if arguments['encrypted']:
		flags | 0b1
		
def connect(arguments):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
		serverConnection, ServerAddress = clientSocket.connect((HOST,PORT))
		sendRequest(arguments, serverConnection, ServerAddress)

def main():
	arguments = parse()
	connect(arguments)


if __name__ == '__main__':
	main()