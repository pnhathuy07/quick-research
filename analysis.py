import pandas as pd
import xlsxwriter
from functions import err, inp, succ, to_front, is_cat
from configurating import enter

import os
import subprocess
import re

dir = os.path.dirname(__file__)

def main(df, info, noninfo, file, folder, name):
    # Setup writer
    succ('Writing Excel Sheets...')
    filepath = folder + '\\' + name + '_analysis.xlsx'
    print(filepath)

    writer = pd.ExcelWriter(filepath, engine='xlsxwriter') # pylint: disable=abstract-class-instantiated

    # Data
    df_all = calculate_frequency(df, noninfo)
    excel(df_all, 'Tất cả', writer, info=info)

    # Groups
    groups = ''
    while True:
        groups = inp('Which column specifies the groups of the subjects?', default=enter)
        if (groups == enter) or (groups in df.columns):
            if (groups != enter):
                df_groups = calculate_frequency(df, noninfo, groups)
                for entry in df_groups[groups].unique():
                    excel(df_groups[df_groups[groups] == entry], entry, writer, info=info)
            break
        err(f"Column '{groups}' does not exist in the list of column names.")

    # Summary Statistics
    s_excel(df, writer, noninfo)

    # Save and Open
    succ('Saving File...')
    print(folder)
    writer.save()

    os.system('start "excel.exe" "' + filepath + '"')
    succ('Launching Excel...')
    
    while input('') == '':
        pass

def calculate_frequency(df, noninfo, groups=enter):
    df2 = pd.DataFrame()

    for col in noninfo:
        if groups != enter:
            df2[col] = df.groupby([groups, col])[col].transform('count')
        else:
            df2[col] = df.groupby(col)[col].transform('count') 

    df['__Freq'] = df2.sum(axis=1)
    df.sort_values('__Freq', ascending=False, inplace=True)
    
    if groups != enter:
        for g in df[groups].unique():
            df.loc[df[groups] == g, :] = cluster(df[df[groups] == g])  
    else:
        df = cluster(df)
    
    df = to_front(df, ['__Freq', '__Class'])
    return df

def cluster(df):
    df['__Class'] = pd.cut(df['__Freq'], bins=6, labels=['F', 'E', 'D', 'C', 'B', 'A'])
    return df

def lastval_group(df, col):
    df = df.reset_index()
    if '__Class' in df.columns:
        
        df = df[~df.duplicated(subset=col, keep='last')]
    else:
        df = df.iloc[[-1]]
    return df.index.tolist()

############################## Excel Writer ##############################

def excel(df, sheetname, writer, startrow=1, startcol=0, info='', title=''):
    df.drop('index', axis=1, errors='ignore', inplace=True)

    sheetname = re.sub(r'(\[|\]|\:|\*|\?|\/|\\)', '', sheetname)
    if len(sheetname) > 28:
        sheetname = sheetname[:28] + '...'

    df.to_excel(writer, sheet_name=sheetname, index=False, startrow=startrow, startcol=startcol)

    workbook  = writer.book
    worksheet = writer.sheets[sheetname]

    max_row, max_col = df.shape

    # Add a filter.
    worksheet.autofilter(startrow, startcol, startrow + max_row, startcol + max_col - 1)
    worksheet.set_row(startrow, 30)

    # Personal information format.
    info_format = workbook.add_format({'color': '#0955ec'})

    if info != '':
        for col in info:
            loc = df.columns.get_loc(col)
            worksheet.conditional_format(startrow + 1, startcol + loc, startrow + max_row + 1, startcol + loc, {'type': 'no_errors', 'format': info_format})

    # Percentage format.
    percentage_format = workbook.add_format({'num_format': '0.0%'})
    if 'Percentage' in df.columns:
        loc = df.columns.get_loc('Percentage')
        worksheet.conditional_format(startrow + 1, startcol + loc, startrow + max_row + 1, startcol + loc, {'type': 'no_errors', 'format': percentage_format})


    # Fit column width
    for idx, col_name in enumerate(df.columns.values):
        series = df[col_name]
        max_len = max((
                series.astype(str).map(len).max(),  # Length of largest item
                len(str(series.name))  # Length of column name/header
                )) + 2  # Adding extra space
        worksheet.set_column(startcol + idx, startcol + idx, max_len)

    # Title
    if title == '': title = sheetname
    title_format = workbook.add_format({'bold': True, 'font_size': 52})
    worksheet.merge_range(xlsxwriter.utility.xl_range(startrow - 1, startcol, startrow - 1, startcol + max_col - 1), title, title_format)

    # Thick borders
    b_border = workbook.add_format(
        {
            'bottom': 1,
            'color': '#000000'
        }
    )
    header_format = workbook.add_format(
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

    for i in lastval_group(df, '__Class'):
        worksheet.conditional_format(xlsxwriter.utility.xl_range(startrow + i + 1, startcol, startrow + i + 1, startcol + max_col - 1), {'type': 'no_errors','format': b_border})

    worksheet.conditional_format(xlsxwriter.utility.xl_range(startrow, startcol, startrow, startcol + max_col - 1), {'type': 'no_errors','format': header_format})
    worksheet.conditional_format(xlsxwriter.utility.xl_range(startrow - 1, startcol + max_col, max_row + 1, startcol + max_col), {'type': 'no_errors','format': l_thick_border})

    if '__Freq' in df.columns:
        loc = df.columns.get_loc('__Freq')
        worksheet.conditional_format(startrow + 1, startcol + loc, startrow + max_row + 1, startcol + loc, {'type': '3_color_scale'})

    # Change selection
    worksheet.set_selection(startrow + max_row, startcol + max_col + 2, startrow + max_row, startcol + max_col + 2)

def s_excel(df, writer, noninfo):
    startcol = 0
    
    for series in noninfo:
        if is_cat(df, series):
            data = pd.DataFrame(df[series].value_counts().reset_index())
            data['Values'] = data['index']
            data['Count'] = data[series]
            data.drop(series, axis=1, inplace=True)
            data['Percentage'] = data['Count'] / data['Count'].sum()
            excel(data, series, writer, startcol=startcol)
            startcol += 2