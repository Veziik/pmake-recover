#! /usr/bin/env python3
import sys
import struct
import pyperclip

def seed_trashlength(key, path):
	sum1 = 0
	for letter in key:
		sum1 += ord(letter)

	sum2 = 0
	for letter in path:
		sum2 += ord(letter)

	return (sum1 ^ sum2)

def parse():

	if len(sys.argv) < 4:
		print("""\nusage: """ +sys.argv[0] + """ <key> <save location> <length>
			-s: show recovered password in shell, off be default
			-e: recover from encrypted file, off by default""")
		sys.exit(0)

	arguments = dict()

	arguments['writePath'] = sys.argv[2] #+ '.card'
	arguments['trashLength'] = seed_trashlength(sys.argv[1], sys.argv[2])
	arguments['length']= int(sys.argv[3])
	arguments['inbytes']= 0
	arguments['showPass'] = False
	
	
	for i in range(0, len(sys.argv)):
		if sys.argv[i] == '-e':
			arguments['inbytes'] = 1
		if sys.argv[i] == '-s':
			arguments['showPass'] = True

	return arguments

def pull(arguments):
	with open('files/' + arguments['writePath'], 'r') as file:
		contents = file.read()
		recovered = contents[arguments['trashLength']:arguments['trashLength']+arguments['length']]
		if not arguments['showPass']:
			pyperclip.copy(recovered)
			print('\nPassword Copied to Clipboard, Try not to paste prematurely')
		else:
			print('\nrecovered: ' + recovered)

def pull_bytes(arguments):
	num = 0
	with open('files/'+arguments['writePath'], 'rb') as file:
		contents = file.read()
		for line in contents:
			print(str(struct.unpack('!i',line)) + str(num))
		recovered = contents[arguments['trashLength']:arguments['trashLength']+arguments['length']]
		if not arguments['showPass']:
			pyperclip.copy(recovered)
			print('\nPassword Copied to Clipboard, Try not to paste prematurely')
		else:
			print('\nrecovered: ' + recovered)
		

def main():

	arguments = parse()
	
	if arguments['inbytes'] == 0:
		pull(arguments)
	if arguments['inbytes'] == 1:
		pull_bytes(arguments)



main()
