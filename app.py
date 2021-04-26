import functions as f
from functions import inp, err, succ
import cleaning as c
import survey

import pandas as pd
import sys

f.credit()

############################## PART A: Importing data ##############################
file = f.dragdrop()
folder, name = str(file.parent), file.name

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
    df = df.drop_duplicates(subset=info, keep='last')
    df = df.reset_index(drop=True)

    succ('Data cleaning completed. Here is the final DataFrame.')
    print(df)

    survey.main(df, info, noninfo, file, folder, name)