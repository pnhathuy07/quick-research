import functions
from functions import err, success, text
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
    # B1: Importing
    file = functions.drag_drop()
    name = file.stem
    folder = str(file.parent).replace("/", "\\") + "\\" + name
    extension = file.suffix

    if file.suffix[1:] != "csv":
        err("Imported data must be a CSV file.")
        functions.quit_app()

    df = pd.read_csv(file, usecols=(lambda x: x not in ["Timestamp", "Dấu thời gian", "index"]))

    if len(df.columns) < 3:
        err("Your data must have at least 3 columns.")
        functions.quit_app()

    if len(df.index) < 6:
        err("Your data must have at least 6 records.")
        functions.quit_app()

    # B2: Cleaning column names
    df = cleaning.column_name_cleaning(df)

    # B3: Data summary
    success("Here is a summary of the columns in your data.")
    df.info(memory_usage='deep')

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
