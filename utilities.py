#! /usr/env/bin python3
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def seedFrontTrashlength(arguments):
	sum1 = 0
	for letter in arguments['key']:
		sum1 += ord(letter)

	sum2 = 0
	for letter in arguments['fileName']:
		sum2 += ord(letter)

	return (sum1 ^ sum2)


def createIV(arguments):
	hashable1 = arguments['hash'] + arguments['fileName']
	return hashlib.sha256(hashable1.encode('utf-8')).hexdigest()[0:16]

def seedBackTrashlength(arguments):
	sum1 = 0
	for letter in arguments['hash']:
		sum1 -= ord(letter)

	sum2 = 0
	for letter in arguments['fileName']:
		sum2 += ord(letter)

	return abs(~(sum1 & sum2))

def findConfigFile():
	file = None
	try:
		file = open('files/config.ini','r' )
	except Exception as e:
		pass
	return file 

def decryptString(arguments, string):
	offset = len(string)%16
	string = string[0:(len(string)-offset)]
	backend = default_backend()
	key = arguments['hash']
	iv = createIV(arguments)
	cipher = Cipher(algorithms.AES(key.encode('utf-8')), modes.CBC(iv.encode('utf-8')), backend=backend)
	decryptor = cipher.decryptor()
	plaintext = decryptor.update(string) + decryptor.finalize()
	return str(plaintext, 'utf-8')

def encryptString(arguments, string):
	offset = len(string)%16
	string = string[0:(len(string)-offset)]
	backend = default_backend()
	key = arguments['hash']
	iv = createIV(arguments)
	cipher = Cipher(algorithms.AES(key.encode('utf-8')), modes.CBC(iv.encode('utf-8')), backend=backend)
	encryptor = cipher.encryptor()
	ct = encryptor.update(string.encode('utf-8')) + encryptor.finalize()
	return ct