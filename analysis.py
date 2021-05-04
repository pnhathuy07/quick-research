from numpy.core.numeric import NaN
import pandas as pd
from functions import err, succ
from configurating import enter

import os
import subprocess

builtin = ['frequency', 'index']

def main(df, info, noninfo, file, folder, name):
    df = calculate_frequency(df, noninfo)

    # Setup writer
    succ('Writing Excel Sheets...')
    filepath = folder + '\\' + name + '_analysis.xlsx'
    print(filepath)

    writer = pd.ExcelWriter(filepath, engine='xlsxwriter') # pylint: disable=abstract-class-instantiated
    excel(df, info, noninfo, 'Data', writer)

    # Save and Open
    succ('Saving File...')
    print(folder)
    writer.save()

    os.system('start "excel.exe" "' + filepath + '"')
    succ('Launching Excel...')
    input('')

def calculate_frequency(df, noninfo):
    df[enter] = enter # Constant value
    df2 = pd.DataFrame()
    for col in noninfo:
        df2[col] = df.groupby(col)[col].transform('count')

    df['frequency'] = df2.sum(axis=1)
    return df

############################## Excel Writer ##############################
def excel(df, info, noninfo, sheetname, writer):
    df.to_excel(writer, sheetname, index=False)

    workbook  = writer.book
    worksheet = writer.sheets[sheetname]

    max_row, max_col = df.shape

    # Add a header format.
    header_format = workbook.add_format({
        'bold': True,
        'border': 0})

    worksheet.autofilter(0, 0, max_row, max_col - 1)
    worksheet.set_row(0, 31, header_format)

    # Personal information format.
    info_format = workbook.add_format({'color': '#548dd4'})

    for col in info:
        loc = df.columns.get_loc(col)
        worksheet.set_column(loc, loc, cell_format=info_format)

    # Built-in format.
    builtin_format = workbook.add_format({'color': '#0955ec', 'bold': True})

    for col in builtin:
        loc = df.columns.get_loc(col)
        worksheet.set_column(loc, loc, cell_format=builtin_format)

    # Fit column width
    for idx, col_name in enumerate(df.columns.values):
        series = df[col_name]
        max_len = max((
                series.astype(str).map(len).max(),  # Length of largest item
                len(str(series.name))  # Length of column name/header
                )) + 2  # Adding extra space
        worksheet.set_column(idx, idx, max_len)