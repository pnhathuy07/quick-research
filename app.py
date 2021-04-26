import functions as f
from functions import inp, err, succ
import cleaning as c

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
mode = inp('Select a mode', 'Finding Trends in a Survey', 'Graphing Data', default='A')

############################## PART C: Finding Trends in a Survey ##############################
if mode == 'A':
    # C1: Extract personal information
    info_cols = c.info_extract(df)