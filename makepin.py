#!/usr/bin/env python3
import sys
import os
import platform
import hashlib
import random
import time
import struct
try:
	import pyperclip
except:
	pass
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from words import *


def replaceWithSymbol(optionalSymbols):
	symbolsToSampleFrom = '1234567890' + optionalSymbols
	return symbolsToSampleFrom[random.randint(0,len(symbolsToSampleFrom)-1)]
	

def replaceWithAlpha():
	alphasToSampleFrom = 'QWERTYUIOPLKJHGFDSAZXCVBNMqwertyuiopasdfghjklzxcvbnm'
	return alphasToSampleFrom[random.randint(0,len(alphasToSampleFrom)-1)]

def addCharacter(optionalSymbols):
	charactersToSampleFrom = '1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM' + optionalSymbols
	return charactersToSampleFrom[random.randint(0,len(charactersToSampleFrom)-1)]

def addWord(wordlist, length):
	if length == -1:
		return wordlist[random.randint(0,len(wordlist)-1)]
	else:
		wordsOfACertainLength = []

		for word in wordlist:
			if len(word) <= length:
				wordsOfACertainLength.append(word)

		return wordsOfACertainLength[random.randint(0,len(wordsOfACertainLength)-1)]

def createIV(arguments):
	hashable1 = arguments['key'] + arguments['fileName']
	return hashlib.sha256(hashable1.encode('utf-8')).hexdigest()[0:16]

def encryptString(arguments, string):
	#print('\n\n\n OFFSET:' + str(len(string)%16) + ' \n\n\n')
	offset = len(string)%16
	string = string[0:(len(string)-offset)]
	backend = default_backend()
	key = arguments['key']
	iv = createIV(arguments)
	cipher = Cipher(algorithms.AES(key.encode('utf-8')), modes.CBC(iv.encode('utf-8')), backend=backend)
	encryptor = cipher.encryptor()
	ct = encryptor.update(string.encode('utf-8')) + encryptor.finalize()
	return ct

def writePlaintextFile(contents, arguments):
	with open('files/'+arguments['fileName'] + arguments['fileExtension'] , 'w') as file:	
		file.write(contents)
		arguments['length'] = str(len(contents))
		if arguments['useClipboard'] > 0:
			pyperclip.copy(contents)
		if arguments['useClipboard'] == 2:
			contents = '[CONTENTS REDACTED]'
		print('\nnew password: ' + contents + '\nlength: '+ arguments['length'] + '\nfile: ' + 'files/'+arguments['fileName'] + '\npadding: False\nencryption: False')

def writePaddedFile(contents, wordlist, arguments):
	front = ''
	back = ''
	writeProtocol = 'w'
	#print('front: ' + str(seedFrontTrashlength()))
	#print('back: ' + str(seedBackTrashlength()))
	frontlen = seedFrontTrashlength()
	backlen = seedBackTrashlength()
	
	if os.path.isfile('files/'+arguments['fileName'] + '.pad'):
		os.remove('files/'+arguments['fileName'] + '.pad')
	if os.path.isfile(arguments['fileName'] + '.enc'):
		os.remove('files/'+arguments['fileName'] + '.enc')

	while (frontlen + arguments['length'] + backlen) % 16 != 0:
		backlen += 1


	if not arguments['words']:
		for i in range(0, frontlen): 
			front += addCharacter(arguments['symbols'])
		
		for i in range(0, backlen): 
			back += addCharacter(arguments['symbols'])
	else:

		while len(front) < frontlen:
			if random.randint(1,6) >= 4:
				front += addWord(wordlist, frontlen - len(front))
			else:
				front += replaceWithSymbol(arguments['symbols'])
		front = front[0:frontlen]

		while len(back) < backlen:
			if random.randint(1,6) >= 4:
				back += addWord(wordlist, backlen - len(back))
			else:
				back += replaceWithSymbol(arguments['symbols'])
		back = back[0:backlen]

	
	finalBlockOfText = (front + contents + back)	


	textEncrypted = False
	if arguments['encrypt'] == 2:
		writeProtocol = 'wb'
		finalBlockOfText = encryptString(arguments, finalBlockOfText)
		textEncrypted = True

	with open('files/' + arguments['fileName'] + arguments['fileExtension'], writeProtocol) as file:
		file.write(finalBlockOfText)
		arguments['length'] = str(len(contents))
		if arguments['useClipboard'] > 0:
			pyperclip.copy(contents)
		if arguments['useClipboard'] == 2:
			contents = '[CONTENTS REDACTED]'
		print('\nnew password: ' + contents + '\nlength: '+ arguments['length'] + '\nfile: ' + 'files/'+arguments['fileName'] + '\npadding: True\nencryption: ' + str(textEncrypted))

def seedFrontTrashlength():
	sum1 = 0
	for letter in sys.argv[1]:
		sum1 += ord(letter)

	sum2 = 0
	for letter in sys.argv[2]:
		sum2 += ord(letter)

	return (sum1 ^ sum2)

def seedBackTrashlength():
	sum1 = 0
	for letter in sys.argv[1]:
		sum1 -= ord(letter)

	sum2 = 0
	for letter in sys.argv[2]:
		sum2 += ord(letter)

	return abs(~(sum1 & sum2))

def parse():

	if len(sys.argv) < 3:
		print("""\nusage: """ + sys.argv[0] + """ <key> <save location> [options]
			\noptions:
			\n-s <string> : symbols to use [none set by default] 
			\n-sA: use set of all possible non-numeric, non alphabetic ascii symbols 
			\n-sR <string>: use all symbols, except those in parameter
			\n-g <integer> : growth factor, -3 < x < 3, influences length of output, default 0
			\n-l <integer> : length limit, truncates output to given size, default infinity
			\n-p: pad, pad with random amount of trash data, false by default
			\n-e: encrypt, pads and encrypts to bytes, false by default, still in development
			\n-w: use words instead of random letter strings for easier memorization, off by default
			\n-q: quick setting for my most common options without words \'-sA -p -g 3 -l 32 -cH\'
			\n-qW: quick setting for my most common options with words \'-sA -p -g 3 -l 32 -w 5 -cH\'
			\n-o: overwite existing file, off by default
			\n-oN: do not write to file, off by default
			\n-c: save to clipboard and show output, off by default
			\n-cH: save to clipboard and hide output, on by default
			\n-cN: don't save to clipboard, on by default
			""")
		sys.exit(0)

	
	arguments = dict()
	arguments['fileName'] = sys.argv[2]# + '.card'
	arguments['pinstr'] = sys.argv[2]+sys.argv[1]
	arguments['growthFactor'] = 3
	arguments['symbols'] = ',./;\\[]!@#$%^&*()_+?|:+-=<>:|{}_'
	arguments['length'] = 16
	arguments['encrypt'] = 2
	arguments['key'] = hashlib.sha256(sys.argv[1].encode('ascii')).hexdigest()[0:32]
	arguments['words'] = True
	arguments['maxWordLength'] = 4
	arguments['useClipboard'] = 2 # 0 = don't use clipboard, 1 = use clipboard but still show, 2 = use clipboard and do not show output 		
	arguments['overwrite'] = False
	arguments['fileExtension'] = '.enc'

	#if True:
	try:
		args = sys.argv
		for i in range(3, len(args)):
			if args[i] == '-q':
				arguments['growthFactor'] = 3
				arguments['symbols'] = ''
				if i+1 < len(args) and not args[i+1].replace('-' , '').isalpha():
					arguments['symbols'] = args[i+1] 
				else:
					arguments['symbols'] = ',./;\\[]!@#$%^&*()_+?|:+-=<>:|{}_'
				arguments['encrypt'] = 2
				arguments['fileExtension'] = '.enc'
				arguments['length'] = 32

			elif args[i] == '-qW':
				arguments['growthFactor'] = 3
				arguments['symbols'] = ''
				if i+1 < len(args) and not args[i+1].replace('-' , '').isalpha():
					arguments['symbols'] = args[i+1] 
				else:
					arguments['symbols'] = ',./;\\[]!@#$%^&*()_+?|:+-=<>:|{}_'
				arguments['encrypt'] = 2
				arguments['fileExtension'] = '.enc'
				arguments['length'] = 16
				arguments['words'] = True
				arguments['maxWordLength'] = 4
			elif args[i] == '-g':
				arguments['growthFactor'] = int(args[i+1])
				if arguments['growthFactor'] > 3 or arguments['growthFactor'] < -3:
					sys.exit(0)
			elif args[i] == '-s':
				arguments['symbols'] = args[i+1]
				arguments['symbols'] = arguments['symbols'].replace('\'', '')
			elif args[i] == '-sR':
				arguments['symbols'] = ',./;\\[]!@#$%^&*()_+?|:+-=<>:|{}_'
				taboos = args[i+1]
				taboos = taboos.replace('\'', '')
				for taboo in taboos:
					arguments['symbols'] = arguments['symbols'].replace(taboo, '')
			elif args[i] == '-sA':
				arguments['symbols'] = ',./;\\[]!@#$%^&*()_+?|:+-=<>:|{}_'
			elif args[i] == '-l':
				arguments['length'] = int(args[i+1])
			elif args[i] == '-p':
				arguments['encrypt'] = 1
				arguments['fileExtension'] = '.pad'
			elif args[i] == '-e':
				arguments['encrypt'] = 2
				arguments['fileExtension'] = '.enc'
			elif args[i] == '-oN':
				arguments['encrypt'] = 3
			elif args[i] == '-o':
				arguments['overwrite'] = True
			elif args[i] == '-cN':
				arguments['useClipboard'] = 0
			elif args[i] == '-c':
				arguments['useClipboard'] = 1
			elif args[i] == '-cH':
				arguments['useClipboard'] = 2
			elif args[i] == '-w':
				arguments['words'] = True
				if i+1 < len(args) and '-' not in args[i+1] and not int(args[i+1]) < 1:
					arguments['maxWordLength'] = int(args[i+1])
						
	except:
	 	print('arguments missing or formatted incorrectly')
	 	sys.exit(0)

	if 'microsoft-x86_64-with-ubuntu' in platform.platform().lower():
		print("Windows Subsystem for Linux detected, showing cleartext")
		arguments['useClipboard'] = 0 

	return arguments


def scrambleWithCharacters(pinhash,arguments):
	i = 0
	while i < len(pinhash):
		random.seed((time.time()-10000)+i)
		if pinhash[i].isalpha():
			if random.randint(1,6) >= 2:
				pinhash = pinhash[i+1:len(pinhash)] + replaceWithAlpha() + pinhash[0:i] 
		random.seed((time.time()-100000)+i)
		if pinhash[i].isdigit():
			if random.randint(1,6) >= 2:
				pinhash =  pinhash[i+1:len(pinhash)] + replaceWithSymbol(arguments['symbols']) + pinhash[0:i]
		random.seed((time.time()-1000000)+i)
		if random.randint(1,6) >= 5 - arguments['growthFactor'] :#and random.randint(1,6) != 1:
			pinhash =  pinhash + addCharacter(arguments['symbols'])
		random.seed((time.time()-10000000)+i)
		if random.randint(1,6) <= 2 - arguments['growthFactor'] :#and random.randint(1,6) != 6:
			pinhash =  pinhash[0:len(pinhash)-1]
		i+=1
		
	if arguments['length'] != -1:
		pinhash = pinhash[0:arguments['length']]

	return pinhash


def scrambleWithWords(pinhash, arguments, wordlist):
	newpass = ''
	stop = False
	i = 0



	if arguments['length'] == -1:
		while (not stop) and (i < len(pinhash)):
			random.seed((time.time()-10000)+i)
			if random.randint(1,6) >= 4:
				if pinhash[i].isalpha():
					newword = addWord(wordlist, arguments['maxWordLength']).capitalize()
					newpass = newpass + newword 
				
				elif(pinhash[i].isdigit()):
					if random.randint(1,6) >= 2:
						newpass = newpass + replaceWithSymbol(arguments['symbols'])
					else:
						newpass = newpass + pinhash[i]
			if random.randint(1,6) >= 2:
				
				pinhash = pinhash[int(len(pinhash)/2):int(len(pinhash))] + pinhash[0:int((len(pinhash)/2)-1)]
			if random.randint(0,len(pinhash)) > len(pinhash) - i:
				stop = True
			i = i+1
	else:
		
		while len(newpass) < arguments['length'] :
			random.seed((time.time()-100)+i)
			if random.randint(1,6) >=4:
				if pinhash[i].isalpha():
				
					newword = addWord(wordlist, arguments['length'] - len(newpass)+1).capitalize()
					
					newpass = newpass + newword
				elif(pinhash[i].isdigit()):
					if random.randint(1,6) >= 2:
						newpass = newpass + replaceWithSymbol(arguments['symbols'])
					else:
						newpass = newpass + pinhash[i]
			random.seed((time.time()-10000)+i)
			if random.randint(1,6) >= 4 :
				pinhash = pinhash[int(len(pinhash)/2):int(len(pinhash))] + pinhash[0:int((len(pinhash)/2))]			
			i = i + 1 
		newpass = newpass[0:arguments['length']]

	
	return newpass

def printWithoutWriting(contents):
	print('\nnew password: ' + contents + '\nlength'+ arguments['length'] + '\nfile: ' + 'none' + '\npadding: true\nencryption: false')

def check_for_existing_files(arguments):
	if os.path.isfile('files/'+arguments['fileName']+arguments['fileExtension']):
		fileName = arguments['fileName']
		print(f'File exists with name {fileName}, exiting')
		sys.exit(0)

def main():
	arguments = parse()
	if not arguments['overwrite']:
		check_for_existing_files(arguments)
	wordlist = ''	
	pinhash = hashlib.sha256(arguments['pinstr'].encode('ascii')).hexdigest()

	if arguments['words']:
		wordlist = importWords('words.txt', arguments['maxWordLength'])
		pinhash = scrambleWithWords(pinhash,arguments, wordlist)
		
	else:
	
		pinhash = scrambleWithCharacters(pinhash,arguments)

	if not os.path.exists('files'):
		os.makedirs('files')

	if arguments['encrypt'] == 0:
		writePlaintextFile(pinhash, arguments)
	elif arguments['encrypt'] == 1 or arguments['encrypt'] == 2:
		writePaddedFile(pinhash, wordlist, arguments)
	elif arguments['encrypt'] == 3:
		printWithoutWriting(pinhash)

if  __name__ == '__main__':
	main()
else:
	print('no main')
