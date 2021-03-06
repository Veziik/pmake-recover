#! /usr/bin/env python3
import sys
import platform
import struct
import hashlib
try:
	import pyperclip
except:
	pass
	
import platform
from helpers import *

def findConfigFile():
	file = None
	try:
		file = open('files/config.ini','r' )
	except Exception as e:
		pass
	return file 

def overrideConfigsWithFile(file, arguments):
	readable = False
	startingIndex = 4
	for line in file:
		filtered_line = line.replace(" ","").replace("\n","").strip()
		if readable and len(line)>2 and '[' not in line:
			line_split = filtered_line.split('=')

			argument_key = line_split[0]
			argument_value = line_split[1]
			arguments[argument_key] = argument_value
			if argument_key == "length" or argument_key == "key":
				startingIndex-=1
		if "[precover]" in filtered_line.lower():
			readable = True
		if "[pmake]" in filtered_line.lower():
			readable = False		
	file.close()
	arguments['startingIndex'] = startingIndex
	return arguments

def showHelpTextAndExit():
	print("""\nusage: """ +sys.argv[0] + """<save location> <key> <length>
			-s: show recovered password in shell, off be default
			-e: recover from encrypted file, on by default
			-eN: recover from non-ecrypted padded file, off by defaut""")
	sys.exit(0)

def parse():
	config_file = findConfigFile()

	if len(sys.argv) < 4 and not config_file:
		showHelpTextAndExit()

	arguments = dict()

	arguments['fileName'] = sys.argv[1]
	arguments['encrypted']= True
	arguments['showPass'] = False
	arguments['startingIndex'] = 4

	arguments = overrideConfigsWithFile(config_file, arguments)


	
	try:
		if not sys.argv[2].isDigit():
			arguments['key'] = sys.argv[2]
	except:
		if "key" not in arguments.keys():
			print("""Key not provided, if you're using a config file, remember to add key=<key>.""")
			showHelpTextAndExit()

	
	try:
		int(sys.argv[3])
		arguments['length'] = sys.argv[3]
	except:
		try:
			int(sys.argv[2])
			arguments['length'] = sys.argv[2]
		except:
			if "length" not in arguments.keys():
				print("""Length not provided, if you're using a config file, remember to add length=<length>.""")
				showHelpTextAndExit()	


	arguments['length'] = int(arguments['length'])
	arguments['trashLength'] = seedFrontTrashlength(arguments)
	arguments['hash'] = hashlib.sha256(arguments['key'].encode('ascii')).hexdigest()[0:32]
	
	for i in range(arguments['startingIndex'], len(sys.argv)):
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
	with open('files/' + arguments['fileName']+fileExtension, readProtocol) as file:
		contents = file.read()

		if arguments['encrypted']:
			contents = decryptString(arguments,contents)
		
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
