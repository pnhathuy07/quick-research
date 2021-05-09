from configurating import separatorStr, bcol
import configurating as config

import re, sys
from pathlib import Path
import numpy as np

############################## Credits ##############################
def sep():
    """Print separator"""
    print(separatorStr)

def credit():
    """Print the credit line (name, version, creator)"""
    print(config.creditLine)
    sep()

############################## User Interface ##############################
def inp(message, *options, assign='', default=''):
    """
    Start an input field
    (message, *options, variable name, default value)
    """
    __ass = ''
    __def = ''
    __opt = ''
    letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') 

    if not assign == '': __ass = f'{assign} = '
    if not default == '': __def = f'{bcol.OKCYAN}[Default: {default}] {bcol.ENDC}\n'
    if not options == (): __opt = f"{bcol.BOLD}(Type {', '.join([' for '.join(map(str, i)) for i in zip(letters, options)])}){bcol.ENDC} "

    result = ''

    failedAttempt = 0
    maxfailedAttempt = 10

    while result == '' or (__opt != '' and not result.upper() in letters[:len(options)]):
        result = input(f'\n{bcol.BOLD}{message}{bcol.ENDC}\n{__opt}{__def}>>> {__ass}').strip()

        if result == '':
            if default != '': result = default.strip()
            else: 
                failedAttempt += 1
                print(f'{bcol.FAIL}You cannot leave this field blank. {bcol.BOLD}({str(failedAttempt)} failed attempt){bcol.ENDC}')
        if __opt != '' and not result.upper() in letters[:len(options)]:
            failedAttempt += 1
            print(f'{bcol.FAIL}Invalid input. You must select one from the options above. {bcol.BOLD}({str(failedAttempt)} failed attempt){bcol.ENDC}')

        if failedAttempt >= maxfailedAttempt: 
            print(f'{bcol.WARNING}Session has ended. Exiting application...{bcol.ENDC}')
            sys.exit()

    if len(options) > 0: result = result.upper()

    return result

def err(message):
    """Print an error message."""
    print(f'\n{bcol.FAIL}{bcol.BOLD}ERROR: {message}{bcol.ENDC}')

def succ(message):
    """Print a success message."""
    print(f'\n{bcol.OKGREEN}{bcol.BOLD}{message}{bcol.ENDC}')

def dragdrop():
    filelist = re.findall(r'[a-zA-Z]:\/[^\\\:\*\?\"\>\<\|]*?\.[\w:]+(?!.*[\w\.])', inp(f'Drag and drop your file here').replace('\\', '/').replace('//', '/'))

    if len(filelist) == 0:
        err('No valid filepath found.')
        quit()

    file = Path(filelist[0])

    if not file.exists():
        err('The file provided does not exist.')
        quit()

    return file

def maxlen(str, nlen=31):
    if len(str) > nlen - 3:
        str = str[:nlen - 3] + '...'
    return str

############################## System Controls ##############################
def quit():
    sys.exit(0)

############################## String ##############################
def aspace(text):
    return text.replace(' ', '')

def to_front(df, col):
    col = [i for i in col if i in df.columns]
    col += [i for i in df.columns if i not in col]
    return df[col]

def is_cat(df, series):
    if series in df.dtypes[df.dtypes == np.object].index:
        return True
    else:
        return False