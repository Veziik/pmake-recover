#! /usr/bin/env python3
import sys
import platform
import struct
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
try:
	import pyperclip
except:
	pass
	
import platform

def seedFrontTrashlength():
	sum1 = 0
	for letter in sys.argv[1]:
		sum1 += ord(letter)

	sum2 = 0
	for letter in sys.argv[2]:
		sum2 += ord(letter)

	return (sum1 ^ sum2)


def createIV(arguments):
	hashable1 = arguments['key'] + arguments['writePath']
	return hashlib.sha256(hashable1.encode('utf-8')).hexdigest()[0:16]

def decryptString(arguments, string):
	backend = default_backend()
	key = arguments['key']
	iv = createIV(arguments)
	cipher = Cipher(algorithms.AES(key.encode('utf-8')), modes.CBC(iv.encode('utf-8')), backend=backend)
	decryptor = cipher.decryptor()
	plaintext = decryptor.update(string) + decryptor.finalize()
	return str(plaintext, 'utf-8')

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
	
	for i in range(4, len(sys.argv)):
		if sys.argv[i] == '-eN':
			arguments['encrypted'] = False
		if sys.argv[i] == '-e':
			arguments['encrypted'] = True
		if sys.argv[i] == '-s':
			arguments['showPass'] = True

	if 'microsoft-x86_64-with-ubuntu' in platform.platform().lower():
		print("Windows Subsystem for Linux detected, showing cleartext")
		arguments['showPass'] = True

	return arguments

def pull(arguments):
	readProtocol = 'r'
	fileExtension = '.pad'
	if arguments['encrypted']:
		readProtocol = 'rb'
		fileExtension = '.enc'
	with open('files/' + arguments['writePath']+fileExtension, readProtocol) as file:
		contents = file.read()

		if arguments['encrypted']:
			contents = decryptString(arguments,contents)

		#print(arguments['trashLength'])
		#print(contents)
		
		recovered = contents[arguments['trashLength']:arguments['trashLength']+arguments['length']]
		if not arguments['showPass']:
			pyperclip.copy(recovered)
			print('\nPassword recovered and copied to clipboard, Try not to paste prematurely\n')
		else:
			print('\nrecovered: ' + recovered)
		

def main():

	arguments = parse()		
	pull(arguments)

if  __name__ == '__main__':
	main()
else:
	print('no main')
