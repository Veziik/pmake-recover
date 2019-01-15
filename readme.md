# pmake-recover

A fast and easy password generator that was coded up in about thee days of casual coding. Not at all secure, though it does a good job of looking random

run mkdir files to create files folder for password files

words file for word functionality taken from https://github.com/dwyl/english-words

file usages:
./pmake <key> <save location> [options] : generates a password according to flags given
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

			\n-qW: quick setting for my most common options with words -sA -p -g 3 -l 32 -w 5
			
./precover <key> <save location> <length of password> : recovers padded password

./showpass : shows password when not padded

./push : allows user to push changes in the program to their own git repos, requires seperate repos for the program and the password files

./pull : allows user to pull the changes from their own repos, requires  seperate repos for the program and the password files

all other files are used for development purposes