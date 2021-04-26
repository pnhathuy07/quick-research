from configurating import separatorStr
import functions as f
from functions import aspace, inp, err, succ

import pandas as pd
import numpy as np
import math

#col_list = data.columns.values.tolist()
keywords = ['name', 'họ và tên', 'tên', 'full name', 'first name', 'last name', 'surname', 'tuổi', 'age', 'how old', 'phone', 'số điện thoại', 'sđt', 'sdt', 'dt', 'đt', 'mobile', 'di động', 'mail', 'email', 'gmail', 'địa chỉ', 'địa chỉ nhà', 'address', 'thành phố', 'quận', 'huyện', 'phường', 'tỉnh', 'thành', 'city', 'province', 'district', 'lớp', 'khối', 'class', 'grade', 'trường', 'school', 'là gì']
blackwords = ['nếu', 'sẽ', 'làm', 'thế nào', 'if', 'how would', 'how do', 'think', 'nghĩ', 'về việc', 'muốn', 'want', 'thích', 'like', 'prefer', 'would you', 'rather', 'chọn', 'choose', 'pick', 'nào', 'option', 'following', 'có', 'không', 'có', 'không', 'theo', 'theo bạn', 'theo em', 'theo anh', 'theo chị', 'theo anh/chị', 'theo anh chị', 'opinion', 'best', 'nhất', 'sau đây', 'sau']

def to_score(word):
    word = aspace(word.lower())

    score = (len(word) - sum([len(k) for k in keywords if aspace(k) in word]) + sum([8 for b in blackwords if aspace(b) in word])) / (0.2 + sum([1 for k in keywords if aspace(k) in word]))
    return score

#ls = np.array(['bạn thích điện thoại gì?', 'số điện thoại của bạn là gì?', 'cho mình xin địa chỉ nhà của bạn nhé', 'họ và tên', 'bạn thích tên nào?', 'bạn học lớp nào?', 'what is your phone number?', 'choose one', 'thành phố của bạn có nhiều rác thải không'])
#ls_mp = np.array(list(map(lambda x: to_score(x), ls)))

#print(ls)
#print(ls_mp)

#print(ls[ls_mp < 16])

def info_extract(df):
    ls = np.array(df.columns)
    ls_mp = np.array(list(map(lambda x: to_score(x), ls)))

    ls = list(ls[ls_mp < 16])
    succ(f'We have recognized that the following columns contain personal information of the subjects\n{ls}')

    confirm = inp('Is this recognition correct?', 'Yes', 'No', default='A')
    if not confirm == 'A':
        while True:
            col = inp('Which column do you want to add or remove?', default='Press Enter to Skip').strip()
            if col == 'Press Enter to Skip': break
            elif col in df.columns:
                if col in ls:
                    ls = ls.remove(col)
                else:
                    ls = ls.append(col)
                succ(f'Here are your columns again\n{ls}')
            else:
                err(f'We cannot find the column \'{col}\' in the imported DataFrame. Please check your spelling and try again (case-sensitive).')

    return ls

def clean_na(df, noninfo):
    hasnull = False
    nullcols = []
    for i in list(noninfo):
        if df[i].isnull().values.any():
            hasnull = True
            nullcols.append(i)

    if hasnull:
        option = inp('There are missing values in your data. Do you want to assign random values to the missing data or delete the whole record that contain missing information?', 'Imputation', 'Removal', default='A')
        if option == 'A':
            for col in nullcols:
                fill_list = [i for i in df[col] if not str(i) == 'nan']
                df[col] = df[col].fillna(pd.Series(np.random.choice(fill_list, size=len(df.index))))
        elif option == 'B':
            df = df.dropna(subset=nullcols, axis=0)

    return df