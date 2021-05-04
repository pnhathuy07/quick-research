import functions as f
from functions import inp, err, succ
import cleaning as c
import analysis

import pandas as pd
import sys
import os

f.credit()

def makedir(folder):
    try:
        os.mkdir(folder, 0o755)
    except OSError:
        pass
    os.startfile('"' + folder + '"')

############################## PART A: Importing data ##############################
file = f.dragdrop()
name = file.stem
folder = str(file.parent).replace('/', '\\') + '\\' + name
extension = file.suffix

if file.suffix[1:] not in ['csv', 'xlsx']:
    err('Imported data must be a CSV/XLSX file.')
    f.quit()

skipcols = ['Timestamp']
df = pd.read_csv(file, usecols=(lambda x: x not in skipcols))

succ('Data has been successfully imported into this DataFrame.')
print(df)

############################## PART B: Select mode ##############################
mode = inp('Select a mode', 'Survey Analysis', 'Data Visualization', default='A')

############################## PART C: Finding Trends in a Survey ##############################
if mode == 'A':
    # C1: Extract personal information
    info = c.info_extract(df)
    noninfo = [i for i in df.columns if i not in info]

    # C2: Clean data
    df = c.clean_na(df, noninfo)
    df.reset_index(inplace=True)

    succ('Data cleaning completed. Here is the final DataFrame.')
    print(df)

    makedir(folder)
    df.to_csv(folder + '\\' + name + extension)

    analysis.main(df, info, noninfo, file, folder, name)