import functions
from functions import err, success, text, mkdir
import branding
import cleaning
import visualization
import analysis
import pandas as pd


def main():
    # -------------------------------- PART A: Credit Line -------------------------------- #
    branding.credit()

    # -------------------------------- PART B: Importing Data -------------------------------- #
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

    if len(df.index) < 10:
        err("Your data must have at least 10 records.")
        functions.quit_app()

    # -------------------------------- PART C: Data Cleaning -------------------------------- #
    # C1: Cleaning column names
    df = cleaning.column_name_cleaning(df)

    # C2: Data summary
    success("Here is a summary of the columns in your data.")
    df.info(memory_usage='deep')

    # C3: Detecting columns with personal information
    info = cleaning.info_columns(df)
    noninfo = [i for i in df.columns if i not in info]

    # C4: Data Cleaning
    df = cleaning.clean_na(df, noninfo)
    df.reset_index(drop=True, inplace=True)

    success("Data cleaning completed. Processed data will be saved.")

    # -------------------------------- PART D: Survey Analysis -------------------------------- #
    # D1: Create directories
    mkdir(folder, True)

    df.to_csv(folder + "\\" + name + extension, index=False)
    success("Data successfully saved to this folder.")
    text(folder)

    mkdir(folder + "\\plots")
    visualization.main(folder)  # Setting up visual engine

    # D2: Survey Analysis
    analysis.main(df, info, noninfo, folder, name)


if __name__ == '__main__':
    main()
