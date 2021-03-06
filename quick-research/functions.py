import re
import sys
import os
from pathlib import Path
from configurations import skip_string, ConsoleColors


# ---------------------------------------- User Interface ---------------------------------------- #
def inp(message, *options, assign="", default=""):
    __ass = ""
    __def = ""
    __opt = ""
    letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    if assign != "":
        __ass = f"{assign} = "
    if default != "":
        __def = f"{ConsoleColors.blue}[Default: {default}] {ConsoleColors.end}\n"
    if options != ():
        __opt = f"{ConsoleColors.bold}(Type {', '.join([' for '.join(map(str, i)) for i in zip(letters, options)])})" \
                f"{ConsoleColors.end} "

    result = ""

    failed_attempt = 0
    max_failed_attempt = 5

    while result == "" or (__opt != "" and result.upper() not in letters[:len(options)]):
        result = input(f"\n{ConsoleColors.bold}{message}{ConsoleColors.end}\n{__opt}{__def}>>> {__ass}").strip()

        if result == "":
            if default != "":
                result = default.strip()
            else:
                failed_attempt += 1
                print(
                    f"{ConsoleColors.red}You cannot leave this field blank.{ConsoleColors.end}")
        if __opt != "" and result.upper() not in letters[:len(options)]:
            failed_attempt += 1
            print(
                f"{ConsoleColors.red}Invalid input. You must select one from the options above.{ConsoleColors.end}")

        if failed_attempt >= max_failed_attempt:
            print(f"{ConsoleColors.warning}Your session has expired. Exiting application...{ConsoleColors.end}")
            sys.exit()

    if len(options) > 0:
        result = result.upper()

    return result


def inp_select(message, selection_list, current_list=None, n_max=0, n_min=0):
    if current_list is None:
        current_list = []

    while True:
        while len(current_list) > n_max > 0:
            current_list.pop(0)

        col = inp(
            "{}\n{}You can either specify by name, or by index.\n\n{}".format(
                message,
                ConsoleColors.end,
                "\n".join(
                    str(x)
                    if x[1] not in current_list
                    else ConsoleColors.green + str(x) + ConsoleColors.end
                    for x in list(enumerate(selection_list))
                ),
            ),
            default=skip_string,
        ).strip()

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


def text(title, *context):
    """Print a normal message."""
    msg_context = "\n".join(str(i) for i in context)
    print(f"\n{ConsoleColors.bold}{title}{ConsoleColors.end}\n{msg_context}")


def err(message):
    """Print an error message."""
    print(f"\n{ConsoleColors.red}{ConsoleColors.bold}ERROR: {message}{ConsoleColors.end}")


def success(message):
    """Print a success message."""
    print(f"\n{ConsoleColors.green}{ConsoleColors.bold}{message}{ConsoleColors.end}")


def drag_drop():
    file_list = re.findall(r"[a-zA-Z]:/[^\\:*?\"><|]*?\.[\w:]+(?!.*[\w.])",
                           inp("Drag and drop your file here").replace("\\", "/").replace("//", "/"))

    if len(file_list) == 0:
        err("No valid filepath found.")
        quit_app()

    file = Path(file_list[0])

    if not file.exists():
        err("The file provided does not exist.")
        quit_app()

    return file


# ---------------------------------------- Validation ---------------------------------------- #
def validate(input_string: str):
    return re.sub(r"([|]|:|\*|\?|/|\\)", "", input_string)


def max_len(input_string: str, n_len=31) -> str:
    if len(input_string) > n_len - 3:
        input_string = input_string[:n_len - 3] + "..."
    return input_string


# ---------------------------------------- System Controls ---------------------------------------- #
def mkdir(folder_name: str, open_folder: bool = False):
    """Create new folders."""
    try:
        os.mkdir(folder_name, 0o755)
    except OSError:
        pass

    if open_folder:
        os.startfile("\"{}\"".format(folder_name))


def quit_app():
    sys.exit(0)


# ---------------------------------------- String ---------------------------------------- #
def remove_spaces(string: str) -> str:
    return string.replace(" ", "")


def to_front(df, col):
    col = [i for i in col if i in df.columns]
    col += [i for i in df.columns if i not in col]
    return df.loc[:, col]
