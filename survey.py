import pandas as pd
import os

def main(df, info, noninfo, file, folder, name):
    df = freq(df, noninfo)
    df.sort_values('Frequency', inplace=True, ascending=False)
    print(df)

def freq(df, noninfo):
    df2 = pd.DataFrame()

    for col in noninfo:
       df[col + 'count'] = df.groupby(col)[col].transform(pd.Series.value_counts)

    df['Frequency'] = df2.sum(axis=1)
    return df

def entries_count(df, noninfo):
    dict = {}
    for col in noninfo:
        dict[col] = {}
        for item in df[col]:
            if item in dict[col].keys():
                dict[col][item] += 1
            else:
                dict[col][item] = 1
    return dict