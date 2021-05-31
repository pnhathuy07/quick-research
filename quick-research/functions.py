import re
import sys
from pathlib import Path
import configurations as config
from configurations import separator_string, skip_string, ConsoleColors


# ---------------------------------------- Credits ---------------------------------------- #
def separator():
    """Print separator"""
    print(separator_string)


def credit():
    """Print the credit line (i.e. name, version, creator)"""
    print(config.creditLine)
    separator()


# ---------------------------------------- User Interface ---------------------------------------- #
def inp(message, *options, assign='', default=''):
    """
    Start an input field
    (message, *options, variable name, default value)
    """
    __ass = ''
    __def = ''
    __opt = ''
    letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    if not assign == '':
        __ass = f'{assign} = '
    if not default == '':
        __def = f'{ConsoleColors.cyan}[Default: {default}] {ConsoleColors.end}\n'
    if not options == ():
        __opt = f"{ConsoleColors.bold}(Type {', '.join([' for '.join(map(str, i)) for i in zip(letters, options)])}){ConsoleColors.end} "

    result = ''

    failed_attempt = 0
    max_failed_attempt = 10

    while result == '' or (__opt != '' and not result.upper() in letters[:len(options)]):
        result = input(f'\n{ConsoleColors.bold}{message}{ConsoleColors.end}\n{__opt}{__def}>>> {__ass}').strip()

        if result == '':
            if default != '':
                result = default.strip()
            else:
                failed_attempt += 1
                print(
                    f'{ConsoleColors.red}You cannot leave this field blank. {ConsoleColors.bold}({str(failed_attempt)} failed attempt)'
                    f'{ConsoleColors.end}')
        if __opt != '' and not result.upper() in letters[:len(options)]:
            failed_attempt += 1
            print(
                f'{ConsoleColors.red}Invalid input. You must select one from the options above. {ConsoleColors.bold}'
                f'({str(failed_attempt)} failed attempt){ConsoleColors.end}')

        if failed_attempt >= max_failed_attempt:
            print(f'{ConsoleColors.warning}Session has ended. Exiting application...{ConsoleColors.end}')
            sys.exit()

    if len(options) > 0:
        result = result.upper()

    return result


def inp_select(message, selection_list, current_list=None, n_max=0, n_min=0):
    if current_list is None:
        current_list = list()

    while True:
        while len(current_list) > n_max > 0:
            current_list.pop(0)

        col = inp("{}\n{}You can either specify by name, or by index.\n\n{}"
                  .format(message, ConsoleColors.end, "\n".join([str(x) if x[1] not in current_list
                                                                 else ConsoleColors.green + str(x) + ConsoleColors.end
                                                                 for x in list(enumerate(selection_list))])),
                  default=skip_string).strip()

        if col in (str(x) for x in range(len(selection_list))):
            col = selection_list[int(col)]

        if col == skip_string:
            if len(current_list) < n_min:
                err("You must select at least {} options.".format(n_min))
            else:
                break
        elif col in selection_list:
            if col in current_list:
                current_list.remove(col)
            else:
                current_list.append(col)
        else:
            err(f"Selection '{col}' does not exist in the list of names and indices.")

    return current_list


def err(message):
    """Print an error message."""
    print(f'\n{ConsoleColors.red}{ConsoleColors.bold}ERROR: {message}{ConsoleColors.end}')


def success(message):
    """Print a success message."""
    print(f'\n{ConsoleColors.green}{ConsoleColors.bold}{message}{ConsoleColors.end}')


def drag_drop():
    file_list = re.findall(r'[a-zA-Z]:/[^\\:*?\"><|]*?\.[\w:]+(?!.*[\w.])',
                           inp(f'Drag and drop your file here').replace('\\', '/').replace('//', '/'))

    if len(file_list) == 0:
        err('No valid filepath found.')
        quit_app()

    file = Path(file_list[0])

    if not file.exists():
        err('The file provided does not exist.')
        quit_app()

    return file


# ---------------------------------------- Validation ---------------------------------------- #
def validate(input_string: str):
    return re.sub(r'([|]|:|\*|\?|/|\\)', '', input_string)


def max_len(input_string: str, n_len=31) -> str:
    if len(input_string) > n_len - 3:
        input_string = input_string[:n_len - 3] + '...'
    return input_string


# ---------------------------------------- System Controls ---------------------------------------- #
def quit_app():
    sys.exit(0)


# ---------------------------------------- String ---------------------------------------- #
def remove_spaces(text: str) -> str:
    return text.replace(' ', '')


def to_front(df, col):
    col = [i for i in col if i in df.columns]
    col += [i for i in df.columns if i not in col]
    return df.loc[:, col]
