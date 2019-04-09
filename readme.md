# pmake-recover

A fast and easy password generator that was coded up in about three days of casual coding. Continually updated throughout the months to add features and streamline code. Not at all secure, though it does a good job of looking random

All passwords will be placed into a driectory named files after running unless otherwise specified

words file for word functionality taken from https://github.com/dwyl/english-words

file usages:

pmake : generates a password according to flags given

	./pmake <key> <save location> [options]
		options:
			
			-s <symbols> : symbols to use [none set by default] 
			
			-sA: use set of all possible non-numeric, non alphabetic ascii symbols 
			
			-sR <symbols>: use all symbols, except those in parameter
			
			-g <integer> : growth factor, -3 < x < 3, influences length of output, default 0

			-l <integer> : length limit, truncates output to given size, default infinity
			
			-p: pad, pad with random amount of trash data, false by default
			
			-e: encrypt, pads and encrypts to bytes, false by default, still in development
			
			-w: use words instead of letter strings for easier memorization
			
			-q: quick setting for my most common options without words -sA -p -g 3 -l 32 

			-qW: quick setting for my most common options with words -sA -p -g 3 -l 32 -w 5

			-o: do not write to file
			
precover : recovers padded password

	 ./precover <key> <save location> <length of password>

pshow : shows password when not padded

	./pshow

push.sh : allows user to push changes in the program to their own git repos, requires seperate repos for the program and the password files
	
	./push.sh <optional message>

pull.sh : allows user to pull the changes from their own repos, requires  seperate repos for the program and the password files
	
	./pull.sh 

list.sh : allows user to search through their files for those which match a given name

	./list.sh <filename>

makepin.py : copy of pmake for dev purposes

recoverpin.py : copy of precover for dev purposes

showpass.py : copy of pshow for dev purposes

words.txt : list of words, used by pmake with -w switch

Makefile : makefile for version control

words.py : py script to control length of words imported to pmake
