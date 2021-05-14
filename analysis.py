import pandas as pd
import numpy as np
from pandas.api.types import is_string_dtype as is_cat
from pandas.api.types import is_numeric_dtype as is_num
import xlsxwriter
from functions import err, inp, succ, to_front, maxlen, validate
import visualization as v
from configurating import enter

import os
import subprocess
import re

dir = os.path.dirname(__file__)

def writer(wb, folder, name):
    succ('Setting up writer...')
    filepath = folder + '\\' + name + f'_{wb}.xlsx'
    print(filepath)

    writer = pd.ExcelWriter(filepath, engine='xlsxwriter') # pylint: disable=abstract-class-instantiated
    return (writer, filepath)

def main(df, info, noninfo, file, folder, name):
    pd.options.mode.chained_assignment = None  # default='warn'

    # Setup writer
    writer_a, filepath_a = writer('analysis', folder, name)
    writer_b, filepath_b = writer('statistics', folder, name)
    
    # Data
    df_all = calculate_frequency(df, noninfo)
    excel(df_all, 'Tất cả', writer_a, info=info)
    excel(df_all[df_all['__Class'].isin(['A', 'B', 'C'])], 'Số đông', writer_a, info=info)
    excel(df_all[df_all['__Class'].isin(['D', 'E', 'F'])], 'Số ít', writer_a, info=info)

    # Groups
    groups = ''
    while True:
        groups = inp('Which column specifies the groups of the subjects?', default=enter)
        if (groups == enter) or (groups in df.columns):
            if (groups != enter):
                df_groups = calculate_frequency(df, noninfo, groups)
                for entry in df_groups[groups].unique():
                    excel(df_groups[df_groups[groups] == entry], '(Group) ' + entry, writer_a, info=info, title='Group: ' + entry, titlesize=38)
            break
        err(f"Column '{groups}' does not exist in the list of column names.")

    # Summary Statistics
    s_excel(df, writer_b, noninfo, groups)

    # Save and Open
    succ('Saving File...')
    print(folder)
    writer_a.save()
    writer_b.save()

    os.system('start "excel.exe" "' + filepath_a + '"')
    os.system('start "excel.exe" "' + filepath_b + '"')
    succ('Launching Excel...')
    
    while input('') == '':
        pass

def calculate_frequency(df, noninfo, groups=enter):
    df2 = pd.DataFrame()

    for col in noninfo:
        if groups != enter:
            df2.loc[:, col] = df.groupby([groups, col])[col].transform('count')
        else:
            df2.loc[:, col] = df.groupby(col)[col].transform('count') 

    df.loc[:, '__Freq'] = df2.sum(axis=1)
    df.sort_values('__Freq', ascending=False, inplace=True)
    
    if groups != enter:
        for g in df[groups].unique():
            df.loc[df[groups] == g, :] = cluster(df[df[groups] == g])  
    else:
        df = cluster(df)
    
    df = to_front(df, ['__Freq', '__Class'])
    return df

def cluster(df):
    df.loc[:, '__Class'] = pd.cut(df['__Freq'], bins=6, labels=['F', 'E', 'D', 'C', 'B', 'A'])
    return df

def lastval_group(df, col):
    df = df.reset_index()
    if '__Class' in df.columns:
        
        df = df[~df.duplicated(subset=col, keep='last')]
    else:
        df = df.iloc[[-1]]
    return df.index.tolist()

############################## Excel Writer ##############################

def excel(df, sheetname, writer, startrow=1, startcol=0, info='', title='', titlesize=58, groups=[], image=None):
    df.drop('index', axis=1, errors='ignore', inplace=True)
    if title == '': title = sheetname

    sheetname = validate(sheetname)
    sheetname = maxlen(sheetname)
    
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
    percentage_format = workbook.add_format({'num_format': '0%'})
    if 'Percentage' in df.columns:
        loc = df.columns.get_loc('Percentage')
        worksheet.conditional_format(startrow + 1, startcol + loc, startrow + max_row + 1, startcol + loc, {'type': 'no_errors', 'format': percentage_format})


    # Fit column width
    for idx, col_name in enumerate(df.columns.values):
        series = df.loc[:, col_name]
        max_len = max((
                series.astype(str).map(len).max(),  # Length of largest item
                len(str(series.name))  # Length of column name/header
                )) + 2  # Adding extra space
        worksheet.set_column(startcol + idx, startcol + idx, max_len)

    # Title
    title_format = workbook.add_format({'bold': True, 'font_size': titlesize, 'fg_color': '#ffffff'})
    worksheet.conditional_format(startrow - 1, startcol, startrow - 1, startcol + max_col - 1, {'type': 'no_errors', 'format': title_format})
    worksheet.write(startrow - 1, startcol, title, title_format)

    # Graph
    if image != None:
        offset = 0
        for i in image:
            worksheet.insert_image(startrow + max_row + 1, startcol, i, {'x_offset': offset, 'y_offset': 2})
            offset += 614

    # Thick borders
    b_border = workbook.add_format(
        {
            'bottom': 1,
            'color': '#000000'
        }
    )
    header_format = workbook.add_format(
        {
            'top': 1,
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
    worksheet.conditional_format(xlsxwriter.utility.xl_range(startrow - 1, startcol + max_col, startrow + max_row, startcol + max_col), {'type': 'no_errors','format': l_thick_border})

    if '__Freq' in df.columns:
        loc = df.columns.get_loc('__Freq')
        worksheet.conditional_format(startrow + 1, startcol + loc, startrow + max_row + 1, startcol + loc, {'type': '3_color_scale'})
    for i in groups:
        loc = df.columns.get_loc(i)
        worksheet.conditional_format(startrow + 1, startcol + loc, startrow + max_row + 1, startcol + loc, {'type': 'data_bar'})

    # Change selection
    worksheet.set_selection(10**4, 10**4, 10**4, 10**4)

def catstat(df, series, groupby='Tất cả'):
    data = pd.DataFrame(df[series].value_counts().reset_index())
    data.loc[:, 'Values'] = data['index']
    data.loc[:, groupby] = data[series]
    data.drop([series], axis=1, errors='ignore', inplace=True)
    data = data.set_index('index')
    return data

def numstat(df, series, groupby='Tất cả', old_data=[]):
    data = pd.DataFrame(old_data)
    data.loc[:, groupby] = df[series].agg(['sum', 'count', 'mean', 'median', 'min', 'max', 'std'])
    return data

def s_excel(df, writer, noninfo, groups=enter):
    for series in df.columns:
        if series not in ['index', '__Freq', '__Class']:
            if is_cat(df[series]):
                if (series in noninfo) or (series in groups):
                    data = catstat(df, series)

                    groups_list = ['Tất cả']
                    if groups != enter:
                        for g in df[groups].unique():
                            data.loc[:, g] = 0
                            data_grouped = catstat(df[df[groups] == g], series, g)
                            data.update(data_grouped)
                        
                        groups_list += list(df[groups].unique())

                        data2 = data.set_index('Values').iloc[:, 1:]
                    else:
                        data2 = data.set_index('Values')
                        
                    excel(data, series, writer, title=series, titlesize=30, groups=groups_list, image=[v.pie(data, 'Values', 'Tất cả', series), v.bar(data2, series)])
            elif is_num(df[series]):
                if (df.loc[:, series].mean() < 500000000) or (series in noninfo):
                    data = numstat(df, series)

                    if groups != enter:
                        for g in df[groups].unique():
                            data = numstat(df[df[groups] == g], series, g, data)

                    data = data.transpose()
                    data = data.reset_index()
                    data.loc[:, 'Groups'] = data['index']
                    data = to_front(data, ['Groups'])
                    data.drop('index', axis=1, inplace=True)

                    excel(data, series, writer, title=series, titlesize=30, image=[i for i in [v.kde(df, series), v.kde(df, series, groups)] if i is not None])
                    