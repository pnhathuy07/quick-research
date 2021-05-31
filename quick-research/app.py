import functions
from functions import err, success
import cleaning
import visualization
import analysis
import pandas as pd
import os


def makedir(folder_name: str, open_folder: bool = False):
    """Create new folders."""
    try:
        os.mkdir(folder_name, 0o755)
    except OSError:
        pass

    if open_folder:
        os.startfile("\"{}\"".format(folder_name))


def main():
    # -------------------------------- PART A: Credit Line -------------------------------- #
    functions.credit()

    # -------------------------------- PART B: Importing Data -------------------------------- #
    file = functions.drag_drop()
    name = file.stem
    folder = str(file.parent).replace("/", "\\") + "\\" + name
    extension = file.suffix

    if file.suffix[1:] != "csv":
        err("Imported data must be a CSV file.")
        functions.quit_app()

    df = pd.read_csv(file, usecols=(lambda x: x not in ["Timestamp", "index"]))

    if len(df.index) < 3:
        err("Your data must have at least 3 records.")
        functions.quit_app()

    success("Data has been successfully imported into this DataFrame.")
    print(df, df.info(), sep="\n\n")

    # -------------------------------- PART C: Survey Analysis -------------------------------- #
    # C1: Extract personal information
    info = cleaning.info_extract(df)
    noninfo = [i for i in df.columns if i not in info]

    # C2: Clean data
    df = cleaning.clean_na(df, noninfo)
    df.reset_index(drop=True, inplace=True)

    success("Data cleaning completed. Here is the final DataFrame.")
    print(df, df.info(), sep="\n\n")

    # C3: Create directories
    makedir(folder, True)
    df.to_csv(folder + "\\" + name + extension, index=False)

    makedir(folder + "\\plots")
    visualization.main(folder)

    # C4: Survey Analysis
    analysis.main(df, info, noninfo, folder, name)


if __name__ == '__main__':
    main()
