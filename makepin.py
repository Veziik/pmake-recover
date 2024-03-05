#!/usr/bin/env python3
import sys
import os
import platform
import random
import time
import struct

try:
    import pyperclip
except:
    pass
from words import *
from helpers import *


def replace_with_symbol(optional_symbols):
    symbols_to_sample_from = '1234567890' + optional_symbols
    return symbols_to_sample_from[random.randint(0, len(symbols_to_sample_from) - 1)]


def replace_with_alpha():
    alphas_to_sample_from = 'QWERTYUIOPLKJHGFDSAZXCVBNMqwertyuiopasdfghjklzxcvbnm'
    return alphas_to_sample_from[random.randint(0, len(alphas_to_sample_from) - 1)]


def add_character(optional_symbols):
    characters_to_sample_from = '1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM' + optional_symbols
    return characters_to_sample_from[random.randint(0, len(characters_to_sample_from) - 1)]


def add_word(word_list, length):
    if length == -1:
        return word_list[random.randint(0, len(word_list) - 1)]
    else:
        words_of_a_certain_length = []

        for word in word_list:
            if len(word) <= length:
                words_of_a_certain_length.append(word)

        return words_of_a_certain_length[random.randint(0, len(words_of_a_certain_length) - 1)]


def write_plaintext_file(contents, arguments):
    with open('files/' + arguments['fileName'] + arguments['fileExtension'], 'w') as file:
        file.write(contents)
        arguments['length'] = str(len(contents))
        if arguments['useClipboard'] > 0:
            pyperclip.copy(contents)
        if arguments['useClipboard'] == 2:
            contents = '[CONTENTS REDACTED]'
        print('\nnew password: ' + contents + '\nlength: ' + arguments['length'] + '\nfile: ' + 'files/' + arguments[
            'fileName'] + '\npadding: False\nencryption: False')


def write_padded_file(contents, word_list, arguments):
    front = ''
    back = ''
    write_protocol = 'w'
    front_pad_length = seedFrontTrashlength(arguments)
    back_pad_length = seedBackTrashlength(arguments)

    if os.path.isfile('files/' + arguments['fileName'] + '.pad'):
        os.remove('files/' + arguments['fileName'] + '.pad')
    if os.path.isfile(arguments['fileName'] + '.enc'):
        os.remove('files/' + arguments['fileName'] + '.enc')

    while (front_pad_length + arguments['length'] + back_pad_length) % 16 != 0:
        back_pad_length += 1

    if not arguments['words']:
        for i in range(0, front_pad_length):
            front += add_character(arguments['symbols'])

        for i in range(0, back_pad_length):
            back += add_character(arguments['symbols'])
    else:

        while len(front) < front_pad_length:
            if random.randint(1, 6) >= 4:
                front += add_word(word_list, front_pad_length - len(front))
            else:
                front += replace_with_symbol(arguments['symbols'])
        front = front[0:front_pad_length]

        while len(back) < back_pad_length:
            if random.randint(1, 6) >= 4:
                back += add_word(word_list, back_pad_length - len(back))
            else:
                back += replace_with_symbol(arguments['symbols'])
        back = back[0:back_pad_length]

    final_block_of_text = (front + contents + back)

    is_text_encrypted = False
    if arguments['encrypt'] == 2:
        write_protocol = 'wb'
        final_block_of_text = encryptString(arguments, final_block_of_text)
        is_text_encrypted = True

    with open('files/' + arguments['fileName'] + arguments['fileExtension'], write_protocol) as file:
        file.write(final_block_of_text)
        arguments['length'] = str(len(contents))
        if arguments['useClipboard'] > 0:
            pyperclip.copy(contents)
        if arguments['useClipboard'] == 2:
            contents = '[CONTENTS REDACTED]'
        print('\nnew password: ' + contents + '\nlength: ' + arguments['length'] + '\nfile: ' + 'files/' + arguments[
            'fileName'] + '\npadding: True\nencryption: ' + str(is_text_encrypted))


def override_configs_with_file(file, arguments):
    readable = False
    for line in file:
        filtered_line = line.replace(" ", "").replace("\n", "").strip()
        if readable and len(line) > 2 and '[' not in line:
            line_split = filtered_line.split('=')
            argument_key = line_split[0]
            argument_value = line_split[1]
            arguments[argument_key] = argument_value
        if "[pmake]" in filtered_line.lower():
            readable = True
        if "[precover]" in filtered_line.lower():
            readable = False
    file.close()
    arguments['startingIndex'] = 2
    return arguments


def show_help_text_and_exit():
    print("""\nusage: """ + sys.argv[0] + """<save location> <key>  [options]
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


def parse():
    config_file = findConfigFile()

    if (len(sys.argv) < 3 and not config_file) or len(sys.argv) < 2:
        show_help_text_and_exit()

    arguments = dict()
    arguments['fileName'] = sys.argv[1]
    arguments['growthFactor'] = 1
    arguments['symbols'] = ',./;\\[]!@#$%^&*()_+?|:+-=<>:|{}_'
    arguments['length'] = -1
    arguments['encrypt'] = 2
    arguments['words'] = True
    arguments['maxWordLength'] = -1
    # 0 = don't use clipboard, 1 = use clipboard but still show, 2 = use clipboard and do not show output
    arguments['useClipboard'] = 2
    arguments['overwrite'] = False
    arguments['fileExtension'] = '.enc'
    arguments['startingIndex'] = 3

    if config_file:
        arguments = override_configs_with_file(config_file, arguments)

    try:
        arguments['key'] = sys.argv[2]
    except IndexError:
        if "key" not in arguments.keys():
            print(f"""Key not provided, if you're using a config file, remember to add key=<key>.""")
            show_help_text_and_exit()

    arguments['pinstr'] = arguments['fileName'] + arguments['key']
    arguments['hash'] = hashlib.sha256(arguments['key'].encode('ascii')).hexdigest()[0:32]

    try:
        args = sys.argv
        for i in range(arguments['startingIndex'], len(args)):
            if args[i] == '-q':
                arguments['growthFactor'] = 3
                arguments['symbols'] = ''
                if i + 1 < len(args) and not args[i + 1].replace('-', '').isalpha():
                    arguments['symbols'] = args[i + 1]
                else:
                    arguments['symbols'] = ',./;\\[]!@#$%^&*()_+?|:+-=<>:|{}_'
                arguments['encrypt'] = 2
                arguments['fileExtension'] = '.enc'
                arguments['length'] = 32
                break

            elif args[i] == '-qW':
                arguments['growthFactor'] = 3
                arguments['symbols'] = ''
                if i + 1 < len(args) and not args[i + 1].replace('-', '').isalpha():
                    arguments['symbols'] = args[i + 1]
                else:
                    arguments['symbols'] = ',./;\\[]!@#$%^&*()_+?|:+-=<>:|{}_'
                arguments['encrypt'] = 2
                arguments['fileExtension'] = '.enc'
                arguments['length'] = 16
                arguments['words'] = True
                arguments['maxWordLength'] = 4
                break
            elif args[i] == '-g':
                arguments['growthFactor'] = int(args[i + 1])
                if arguments['growthFactor'] > 3 or arguments['growthFactor'] < -3:
                    sys.exit(0)
            elif args[i] == '-s':
                arguments['symbols'] = args[i + 1]
                arguments['symbols'] = arguments['symbols'].replace('\'', '')
            elif args[i] == '-sR':
                arguments['symbols'] = ',./;\\[]!@#$%^&*()_+?|:+-=<>:|{}_'
                taboos = args[i + 1]
                taboos = taboos.replace('\'', '')
                for taboo in taboos:
                    arguments['symbols'] = arguments['symbols'].replace(taboo, '')
            elif args[i] == '-sA':
                arguments['symbols'] = ',./;\\[]!@#$%^&*()_+?|:+-=<>:|{}_'
            elif args[i] == '-l':
                arguments['length'] = int(args[i + 1])
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
                if i + 1 < len(args) and '-' not in args[i + 1] and not int(args[i + 1]) < 1:
                    arguments['maxWordLength'] = int(args[i + 1])
            elif args[i] == '-h':
                show_help_text_and_exit()

    except Exception as e:
        print(f'arguments missing or formatted incorrectly: {e}')
        show_help_text_and_exit()

    if 'microsoft-x86_64-with-ubuntu' in platform.platform().lower():
        print("Windows Subsystem for Linux 1 detected, showing cleartext")
        arguments['useClipboard'] = 0

    arguments['growthFactor'] = int(arguments['growthFactor'])
    arguments['length'] = int(arguments['length'])
    arguments['encrypt'] = int(arguments['encrypt'])
    arguments['maxWordLength'] = int(arguments['maxWordLength'])
    arguments['useClipboard'] = int(arguments['useClipboard'])
    arguments['startingIndex'] = int(arguments['startingIndex'])

    return arguments


def scrambleWithCharacters(pinhash, arguments):
    i = 0
    while i < len(pinhash):
        random.seed((time.time() - 10000) + i)
        if pinhash[i].isalpha():
            if random.randint(1, 6) >= 2:
                pinhash = pinhash[i + 1:len(pinhash)] + replace_with_alpha() + pinhash[0:i]
        random.seed((time.time() - 100000) + i)
        if pinhash[i].isdigit():
            if random.randint(1, 6) >= 2:
                pinhash = pinhash[i + 1:len(pinhash)] + replace_with_symbol(arguments['symbols']) + pinhash[0:i]
        random.seed((time.time() - 1000000) + i)
        if random.randint(1, 6) >= 5 - arguments['growthFactor']:  # and random.randint(1,6) != 1:
            pinhash = pinhash + add_character(arguments['symbols'])
        random.seed((time.time() - 10000000) + i)
        if random.randint(1, 6) <= 2 - arguments['growthFactor']:  # and random.randint(1,6) != 6:
            pinhash = pinhash[0:len(pinhash) - 1]
        i += 1

    if arguments['length'] != -1:
        pinhash = pinhash[0:arguments['length']]

    return pinhash


def scrambleWithWords(pinhash, arguments, wordlist):
    newpass = ''
    stop = False
    i = 0

    if arguments['length'] == -1:
        while (not stop) and (i < len(pinhash)):
            random.seed((time.time() - 10000) + i)
            if random.randint(1, 6) >= 4:
                if pinhash[i].isalpha():
                    newword = add_word(wordlist, int(arguments['maxWordLength'])).capitalize()
                    newpass = newpass + newword

                elif (pinhash[i].isdigit()):
                    if random.randint(1, 6) >= 2:
                        newpass = newpass + replace_with_symbol(arguments['symbols'])
                    else:
                        newpass = newpass + pinhash[i]
            if random.randint(1, 6) >= 2:
                pinhash = pinhash[int(len(pinhash) / 2):int(len(pinhash))] + pinhash[0:int((len(pinhash) / 2) - 1)]
            if random.randint(0, len(pinhash)) > len(pinhash) - i:
                stop = True
            i = i + 1
    else:

        while len(newpass) < int(arguments['length']):
            random.seed((time.time() - 100) + i)
            if random.randint(1, 6) >= 4:
                if pinhash[i].isalpha():

                    newword = add_word(wordlist, int(arguments['length']) - len(newpass) + 1).capitalize()

                    newpass = newpass + newword
                elif (pinhash[i].isdigit()):
                    if random.randint(1, 6) >= 2:
                        newpass = newpass + replace_with_symbol(arguments['symbols'])
                    else:
                        newpass = newpass + pinhash[i]
            random.seed((time.time() - 10000) + i)
            if random.randint(1, 6) >= 4:
                pinhash = pinhash[int(len(pinhash) / 2):int(len(pinhash))] + pinhash[0:int((len(pinhash) / 2))]
            i = i + 1
        newpass = newpass[0:int(arguments['length'])]

    return newpass


def print_without_writing(contents, arguments):
    print('\nnew password: ' + contents + '\nlength' + arguments[
        'length'] + '\nfile: ' + 'none' + '\npadding: true\nencryption: false')


def check_for_existing_files(arguments):
    if os.path.isfile('files/' + arguments['fileName'] + arguments['fileExtension']):
        file_name = arguments['fileName']
        print(f'File exists with name {file_name}, exiting')
        sys.exit(0)


def main():
    arguments = parse()
    if not arguments['overwrite']:
        check_for_existing_files(arguments)
    wordlist = ''
    pinhash = hashlib.sha256(arguments['pinstr'].encode('ascii')).hexdigest()

    if arguments['words']:
        wordlist = importWords('words.txt', int(arguments['maxWordLength']))
        pinhash = scrambleWithWords(pinhash, arguments, wordlist)

    else:
        pinhash = scrambleWithCharacters(pinhash, arguments)

    if not os.path.exists('files'):
        os.makedirs('files')

    if int(arguments['encrypt']) == 0:
        write_plaintext_file(pinhash, arguments)
    elif int(arguments['encrypt']) == 1 or int(arguments['encrypt']) == 2:
        write_padded_file(pinhash, wordlist, arguments)
    elif int(arguments['encrypt']) == 3:
        print_without_writing(pinhash, arguments)


if __name__ == '__main__':
    main()
else:
    print('no main')
