#! /usr/bin/env python3
import sys

try:
    import pyperclip
    SUPPORTS_PYPERCLIP = True
except:
    SUPPORTS_PYPERCLIP = False

import platform
from helpers import *


def find_config_file():
    file = None
    try:
        file = open('files/config.ini', 'r')
    except Exception as e:
        pass
    return file


def override_configs_with_file(file, arguments):
    readable = False
    starting_index = 4
    for line in file:
        filtered_line = line.replace(" ", "").replace("\n", "").strip()
        if readable and len(line) > 2 and '[' not in line:
            line_split = filtered_line.split('=')

            argument_key = line_split[0]
            argument_value = line_split[1]
            arguments[argument_key] = argument_value
            if argument_key == "length" or argument_key == "key":
                starting_index -= 1
        if "[precover]" in filtered_line.lower():
            readable = True
        if "[pmake]" in filtered_line.lower():
            readable = False
    file.close()
    arguments['startingIndex'] = starting_index
    return arguments


def show_help_text_and_exit():
    print("""\nusage: """ + sys.argv[0] + """<save location> <key> <length>
			-s: show recovered password in shell, off be default
			-e: recover from encrypted file, on by default
			-eN: recover from non-ecrypted padded file, off by defaut""")
    sys.exit(0)


def parse():
    config_file = find_config_file()

    if len(sys.argv) < 4 and not config_file:
        show_help_text_and_exit()

    arguments = dict()

    arguments['fileName'] = sys.argv[1]
    arguments['encrypted'] = True
    arguments['showPass'] = False
    arguments['startingIndex'] = 4

    arguments = override_configs_with_file(config_file, arguments)
    try:
        if not sys.argv[2].isdigit() and not arguments['key']:
            arguments['key'] = sys.argv[2]
    except IndexError:
        if "key" not in arguments.keys():
            print("""Key not provided, if you're using a config file, remember to add key=<key>.""")
            show_help_text_and_exit()

    try:
        int(sys.argv[3])
        arguments['length'] = sys.argv[3]
    except (IndexError, ValueError):
        try:
            int(sys.argv[2])
            arguments['length'] = sys.argv[2]
        except (IndexError, ValueError):
            if "length" not in arguments.keys():
                print("""Length not provided, if you're using a config file, remember to add length=<length>.""")
                show_help_text_and_exit()

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

    if not SUPPORTS_PYPERCLIP:
        print("Platform does not support pyperclip, showing password in shell.")
        arguments['showPass'] = True

    return arguments


def pull(arguments):
    read_protocol = 'r'
    file_extension = '.pad'
    if arguments['encrypted']:
        read_protocol = 'rb'
        file_extension = '.enc'
    with open('files/' + arguments['fileName'] + file_extension, read_protocol) as file:
        contents = file.read()

        if arguments['encrypted']:
            contents = decryptString(arguments, contents)

        recovered = contents[arguments['trashLength']:arguments['trashLength'] + arguments['length']]
        if not arguments['showPass']:
            pyperclip.copy(recovered)
            print('\nPassword recovered and copied to clipboard, Try not to paste prematurely\n')
        else:
            print('\nrecovered: ' + recovered)


def main():
    arguments = parse()
    pull(arguments)


if __name__ == '__main__':
    main()
else:
    print('no main')
