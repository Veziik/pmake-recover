#! /usr/bin/env python3
import sys
import struct

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
			""")
		sys.exit(0)

	

	writepath = sys.argv[2] #+ '.card'
	trashlength = seed_trashlength(sys.argv[1], sys.argv[2])
	length = int(sys.argv[3])
	inbytes = 0
	
	for i in range(0, len(sys.argv)):
		if sys.argv[i] == '-b':
			inbytes = 1

	return (trashlength, length, writepath, inbytes)

def pull(trashlength, length, filename):
	with open('files/' +filename, 'r') as file:
		contents = file.read()
		print('\nrecovered: ' + contents[trashlength:trashlength+length])

def pull_bytes(trashlength, length, filename):
	num = 0
	with open('files/'+filename, 'rb') as file:
		contents = file.read()
		for line in contents:
			print(str(struct.unpack('!i',line)) + str(num))

		print('\nrecovered: ' + contents[trashlength:trashlength+length])

def main():

	(trashlength, length, filename, inbytes) = parse()
	
	if inbytes == 0:
		pull(trashlength, length, filename)
	if inbytes == 1:
		pull_bytes(trashlength, length, filename)



main()
