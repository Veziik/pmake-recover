#!/usr/bin/env python3
import sys
import hashlib
import random
import time
import struct
from words import *


def replace_with_symbol(optional):
	symbols = '1234567890' + optional
	return symbols[random.randint(0,len(symbols)-1)]
	

def replace_with_alpha():
	symbols = 'QWERTYUIOPLKJHGFDSAZXCVBNMqwertyuiopasdfghjklzxcvbnm'
	return symbols[random.randint(0,len(symbols)-1)]

def add_symbol(optional):
	symbols = '1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM' + optional
	return symbols[random.randint(0,len(symbols)-1)]

def add_word(words, length):
	if length == -1:
		return words[random.randint(0,len(words)-1)]
	else:
		words_of_a_certain_length = []

		for word in words:
			if len(word) <= length:
				words_of_a_certain_length.append(word)

		return words_of_a_certain_length[random.randint(0,len(words_of_a_certain_length)-1)]


def write_to_file(filename, contents):
	with open('files/'+filename , 'w') as file:	
		file.write(contents)
		print('\nnew password: ' + contents + '\nlength: '+ str(len(contents)) + '\nfile: ' + 'files/'+filename + '\npadding: false\nencryption: false')

def write_padded(filename, contents, trashlen, optional, words, wordlist):
	front = ''
	back = ''
	if not words:
		for i in range(0, trashlen): 
			front += add_symbol(optional)
		
		for i in range(0, trashlen): 
			back += add_symbol(optional)
	else:
		while len(front) < trashlen:
			if random.randint(1,6) >= 4:
				front += add_word(wordlist, trashlen - len(front))
			else:
				front += replace_with_symbol(optional)
		front = front[0:trashlen]

		while len(back) < trashlen:
			if random.randint(1,6) >= 4:
				back += add_word(wordlist, trashlen - len(back))
			else:
				back += replace_with_symbol(optional)
		back = front[0:trashlen]

	with open('files/' + filename, 'w') as file:
		file.write(front + contents + back)
		print('\nnew password: ' + contents + '\nlength: '+ str(len(contents)) + '\nfile: ' + 'files/'+filename + '\npadding: true\nencryption: false')

def write_encrypted(filename, contents, trashlen, optional):
	
	front = ''
	for i in range(0, trashlen): 
		front += add_symbol(optional)
	back = ''
	for i in range(0, trashlen): 
		back += add_symbol(optional)

	with open('files/' + filename, 'wb') as file:
		full = front + contents + back
		for char in full:
			file.write(struct.pack('!i', ord(char)))
		print('\nnew password: ' + contents + '\nlength: '+ str(len(contents)) + '\nfile: ' + 'files/'+filename + '\npadding: true\nencryption: true')

def seed_trashlength(key, path):
	sum1 = 0
	for letter in key:
		sum1 += ord(letter)

	sum2 = 0
	for letter in path:
		sum2 += ord(letter)

	return (sum1 ^ sum2)

def parse():

	if len(sys.argv) < 3:
		print("""\nusage: """ + sys.argv[0] + """ <key> <save location> [options]
			\noptions:
			\n-s <symbols> : symbols to use [none set by default] 
			\n-sA: use set of all possible non-numeric, non alphabetic ascii symbols 
			\n-sR <symbols>: use all symbols, except those in parameter
			\n-g <integer> : growth factor, -3 < x < 3, influences length of output, default 0
			\n-l <integer> : length limit, truncates output to given size, default infinity
			\n-p: pad, pad with random amount of trash data, false by default
			\n-e: encrypt, pads and encrypts to bytes, false by default, still in development
			\n-w: use words instead of letter strings for easier memorization
			""")
		sys.exit(0)

	

	writepath = sys.argv[2]# + '.card'
	pinstr = sys.argv[2]+sys.argv[1]
	growthfactor = 0
	symbols = ''
	length = -1
	encrypt = 0
	trashlength = 0
	words = False
	maxwordlength = -1
	#if True:
	try:
		for i in range(0, len(sys.argv)):
			if sys.argv[i] == '-g':
				growthfactor = int(sys.argv[i+1])
				if growthfactor > 3 or growthfactor < -3:
					exit(1)
			elif sys.argv[i] == '-s':
				symbols = sys.argv[i+1]
				symbols = symbols.replace('\'', '')
			elif sys.argv[i] == '-sR':
				symbols = ',./;\\[]!@#$%^&*()_+?|:+-=<>:|{}_'
				taboos = sys.argv[i+1]
				taboos = taboos.replace('\'', '')
				for taboo in taboos:
					symbols = symbols.replace(taboo, '')
			elif sys.argv[i] == '-sA':
				symbols = ',./;\\[]!@#$%^&*()_+?|:+-=<>:|{}_'
			elif sys.argv[i] == '-l':
				length = int(sys.argv[i+1])
			elif sys.argv[i] == '-p':
				encrypt = 1
				trashlength = seed_trashlength(sys.argv[1], sys.argv[2])
			elif sys.argv[i] == '-e':
				encrypt = 2
				trashlength = seed_trashlength(sys.argv[1], sys.argv[2])
			elif sys.argv[i] == '-w':
				words = True
				if i+1 < len(sys.argv) and '-' not in sys.argv[i+1] and not int(sys.argv[i+1]) < 1:
					maxwordlength = int(sys.argv[i+1])
						
	except:
	 	print('arguments missing or formatted incorrectly')
	 	exit(1)	


	#print(trashlength)
	return (writepath, pinstr, growthfactor, symbols, length, encrypt, trashlength, words, maxwordlength)


def scramble_hash(pinhash, symbols, growthfactor):
	i = 0
	while i < len(pinhash):
		random.seed((time.time()-10000)+i)
		if pinhash[i].isalpha():
			if random.randint(1,6) >= 2:
				pinhash = pinhash[i+1:len(pinhash)] + replace_with_alpha() + pinhash[0:i] 
		random.seed((time.time()-100000)+i)
		if pinhash[i].isdigit():
			if random.randint(1,6) >= 2:
				pinhash =  pinhash[i+1:len(pinhash)] + replace_with_symbol(symbols) + pinhash[0:i]
		random.seed((time.time()-1000000)+i)
		if random.randint(1,6) >= 5 - growthfactor :#and random.randint(1,6) != 1:
			pinhash =  pinhash + add_symbol(symbols)
		random.seed((time.time()-10000000)+i)
		if random.randint(1,6) <= 2 - growthfactor :#and random.randint(1,6) != 6:
			pinhash =  pinhash[0:len(pinhash)-1]
		i+=1

	return pinhash


def scramble_words(pinhash, symbols, length, growthfactor, wordlist):
	newpass = ''
	stop = False
	i = 0



	if length == -1:
		while (not stop) and (i < len(pinhash)):
			random.seed((time.time()-10000)+i)
			if random.randint(1,6) >= 4:
				if pinhash[i].isalpha():
					newword = add_word(wordlist, length).capitalize()
					newpass = newpass + newword 
				
				elif(pinhash[i].isdigit()):
					if random.randint(1,6) >= 2:
						newpass = newpass + replace_with_symbol(symbols)
					else:
						newpass = newpass + pinhash[i]
			if random.randint(1,6) >= 2:
				
				pinhash = pinhash[int(len(pinhash)/2):int(len(pinhash))] + pinhash[0:int((len(pinhash)/2)-1)]
			if random.randint(0,len(pinhash)) > len(pinhash) - i:
				stop = True
			i = i+1
	else:
		
		while len(newpass) < length :
			random.seed((time.time()-100)+i)
			if random.randint(1,6) >=4:
				if pinhash[i].isalpha():
				
					newword = add_word(wordlist, length - len(newpass)+1).capitalize()
					
					newpass = newpass + newword
				elif(pinhash[i].isdigit()):
					if random.randint(1,6) >= 2:
						newpass = newpass + replace_with_symbol(symbols)
					else:
						newpass = newpass + pinhash[i]
			random.seed((time.time()-10000)+i)
			if random.randint(1,6) >= 4 :
				pinhash = pinhash[int(len(pinhash)/2):int(len(pinhash))] + pinhash[0:int((len(pinhash)/2))]			
			i = i + 1 
		newpass = newpass[0:length]

	
	return newpass

def truncate(pinhash, length):
	return pinhash[0:length]

def main():
	(writepath, pinstr, growthfactor, symbols, length, encrypt, trashlength, words, maxwordlength) = parse()	
	wordlist = ''	
	pinhash = hashlib.sha256(pinstr.encode('ascii')).hexdigest()

	if words:
		wordlist = importWords('words.txt', maxwordlength)
		pinhash = scramble_words(pinhash,symbols, length, growthfactor, wordlist)
		
	else:
	
		pinhash = scramble_hash(pinhash,symbols,growthfactor)

		if length != -1 and len(pinhash) > length:
			pinhash = truncate(pinhash, length)

	if encrypt == 0:
		write_to_file(writepath, pinhash)
	elif encrypt == 1:
		write_padded(writepath, pinhash, trashlength, symbols, words, wordlist)
	elif encrypt == 2:
		write_encrypted(writepath, pinhash, trashlength, symbols)

main()
