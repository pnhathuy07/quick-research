import pandas as pd
import xlsxwriter
from functions import err, succ

import os
import subprocess

entries = {}
def main(df, info, noninfo, file, folder, name):
    global entries
    entries = entries_count(df, noninfo)

    df = freq(df, noninfo)

    # Setup writer
    print('Writing Excel Sheets...')
    filepath = folder + '\\' + name + '_analysis.xlsx'
    writer = pd.ExcelWriter(filepath, engine='xlsxwriter') # pylint: disable=abstract-class-instantiated

    exl(df, 'Data', writer)

    # 7: Save and Open
    succ('Saving File...')
    writer.save()

    os.startfile('"' + folder + '"')
    os.startfile(filepath)
    succ('Launching Excel...')

def freq(df, noninfo):
    global entries
    df2 = pd.DataFrame()

    for col in noninfo:
       df2[col] = df[col].apply(lambda x: entries[col][x])

    df['Frequency'] = df2.sum(axis=1)
    return df

def entries_count(df, noninfo):
    dict = {}
    for col in noninfo:
        dict[col] = {}
        value_counts = df[col].value_counts()
        for item in value_counts.index:
            dict[col][item] = value_counts[item]
    return dict

############################## Excel Writer ##############################
def exl(df, sheetname, writer):
    df.to_excel(writer, sheet_name=sheetname, index=False)

    worksheet = writer.sheets[sheetname]

    for idx, col_name in enumerate(df.columns.values):
        series = df[col_name]
        max_len = max((
                series.astype(str).map(len).max(),  # Length of largest item
                len(str(series.name))  # Length of column name/header
                )) + 2  # Adding extra space
        worksheet.set_column(idx, idx, max_len)

    max_row, max_col = df.shape

    df.to_excel(writer, sheet_name='Sheet1', index=False)
    worksheet.autofilter(0, 0, max_row, max_col - 1)

def writeexcel(df, sheetname, writer, mode=1, startwithrow=1):
    df.to_excel(writer, sheet_name=sheetname, index=False, startrow=startwithrow)

    workbook  = writer.book
    worksheet = writer.sheets[sheetname]

    for idx, col_name in enumerate(df.columns.values):
        series = df[col_name]
        max_len = max((
                series.astype(str).map(len).max(),  # Length of largest item
                len(str(series.name))  # Length of column name/header
                )) + 2  # Adding extra space
        worksheet.set_column(idx, idx, max_len)

    if mode == 1:
        worksheet.conditional_format(f'A{startwithrow + 1}:A{len(df.index) + startwithrow + 1}', {'type': '3_color_scale'})

    ###
    b_separator_border = workbook.add_format(
        {
            'bottom': 1,
            'color': '#000000'
        }
    )
    b_thick_border = workbook.add_format(
        {
            'bottom': 2,
            'color': '#000000'
        }
    )
    l_thick_border = workbook.add_format(
        {
            'left': 2,
            'color': '#000000'
        }
    )
    header_format = workbook.add_format({'bold': True, 'font_size': 52})
    ###
    for i in lastvals_dfgroup(df, 'Frequency'):
        worksheet.conditional_format(xlsxwriter.utility.xl_range(i + startwithrow + 1, 0, i + startwithrow + 1, len(df.columns) - 1), {'type': 'no_errors','format': b_separator_border})

    # Thick borders
    worksheet.conditional_format(xlsxwriter.utility.xl_range(startwithrow, 0, startwithrow, len(df.columns) - 1), {'type': 'no_errors','format': b_thick_border})
    worksheet.conditional_format(xlsxwriter.utility.xl_range(startwithrow - 1, len(df.columns), len(df.index) + 1, len(df.columns)), {'type': 'no_errors','format': l_thick_border})

    # Header
    worksheet.merge_range(xlsxwriter.utility.xl_range(0, 0, 0, len(df.columns) - 1), sheetname, header_format)

    # Change selection
    worksheet.set_selection(len(df.index), len(df.columns) + 2, len(df.index), len(df.columns) + 2)

def lastvals_dfgroup(df, col):
    df = df.reset_index()
    df = df[~df.duplicated(subset=col, keep='last')]
    return df.index.tolist()