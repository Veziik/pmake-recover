#! /usr/env/bin python3
import os

def importWords(filename, maxwordlength):
	newwordlist = []
	with open(filename, 'r') as file:
		for line in file:
			line = line.replace('\n', '')
			if maxwordlength == -1 or len(line) <= maxwordlength:
				newwordlist.append(line.title())

	return newwordlist