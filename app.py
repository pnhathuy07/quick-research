import functions
from functions import inp, err, success
import cleaning
import visualization
import analysis

import pandas as pd
import os


def makedir(folder_name: str):
    """Create new folders."""
    try:
        os.mkdir(folder_name, 0o755)
    except OSError:
        pass
    os.startfile("\"{}\"".format(folder_name))


# ---------------------------------------- PART A: Write credit line ---------------------------------------- #
functions.credit()


# ---------------------------------------- PART B: Importing data ---------------------------------------- #
file = functions.drag_drop()
name = file.stem
folder = str(file.parent).replace("/", "\\") + "\\" + name
extension = file.suffix

if file.suffix[1:] != "csv":
    err("Imported data must be a CSV file.")
    functions.quit_app()

df = pd.read_csv(file, usecols=(lambda x: x not in ["Timestamp"]))

success("Data has been successfully imported into this DataFrame.")
print(df)

# ---------------------------------------- PART C: Select mode ---------------------------------------- #
mode = inp("Select a mode", "Survey Analysis", "Data Visualization", default="A")

# ---------------------------------------- PART D: Finding Trends in a Survey ---------------------------------------- #
if mode == "A":
    # C1: Extract personal information
    info = cleaning.info_extract(df)
    noninfo = [i for i in df.columns if i not in info]

    # C2: Clean data
    df = cleaning.clean_na(df, noninfo)
    df.reset_index(inplace=True)

    success("Data cleaning completed. Here is the final DataFrame.")
    print(df)

    makedir(folder)
    df.to_csv(folder + "\\" + name + extension)

    makedir(folder + "\\plots")
    visualization.main(folder)

    analysis.main(df, info, noninfo, folder, name)
elif mode == "B":
    success("Data Visualization coming soon!")
