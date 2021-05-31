from functions import remove_spaces, inp, success, inp_select
import pandas as pd
import numpy as np

keywords = ("name", "họ và tên", "tên", "full name", "first name", "last name", "surname", "tuổi", "age", "how old",
            "phone", "số điện thoại", "sđt", "sdt", "dt", "đt", "mobile", "di động", "mail", "email", "gmail",
            "địa chỉ", "địa chỉ nhà", "address", "thành phố", "quận", "huyện", "phường", "tỉnh", "thành", "city",
            "province", "district", "lớp", "khối", "class", "grade", "trường", "school", "là gì", "giới tính", "gender",
            "sex")

blacklisted_words = ("nếu", "sẽ", "làm", "thế nào", "if", "how would", "how do", "think", "nghĩ", "về việc", "muốn",
                     "want", "thích", "interested", "like", "prefer", "would you", "rather", "chọn", "choose", "pick",
                     "nào", "option", "following", "có", "không", "có", "không", "theo", "theo bạn", "theo em",
                     "theo anh", "theo chị", "theo anh/chị", "theo anh chị", "opinion", "best", "nhất", "sau đây",
                     "sau")


def to_score(word):
    word = remove_spaces(word.lower())

    score = (len(word) - sum([len(k) for k in keywords if remove_spaces(k) in word]) + sum(
        [8 for b in blacklisted_words if remove_spaces(b) in word])) / (
                    0.2 + sum([1 for k in keywords if remove_spaces(k) in word]))
    return score


def info_extract(df):
    ls = np.array(df.columns)
    ls_mp = np.array(list(map(lambda x: to_score(x), ls)))

    ls = list(ls[ls_mp < 16])
    success(f"We have recognized that the following columns contain personal information of the subjects\n{ls}")

    confirm = inp("Is this recognition correct?", "Yes", "No", default="A")
    if not confirm == "A":
        ls = inp_select("Which column do you want to add or remove?", df.columns.tolist(), current_list=ls,
                        n_max=len(df.columns) - 1)
        success(f"Here are your info columns again\n{ls}")

    return ls


def clean_na(df, noninfo):
    has_null = False
    null_columns = list()
    for i in list(noninfo):
        if df[i].isnull().values.any():
            has_null = True
            null_columns.append(i)

    if has_null:
        option = inp(
            "There are missing values in your data. Do you want to leave missing values blank, assign random values "
            "to the missing data or delete the whole record that contain missing information?",
            "Leave Blank", "Impute", "Remove", default="A")
        if option == "B":
            for col in null_columns:
                fill_list = [i for i in df[col] if not str(i) == "nan"]
                df[col] = df[col].fillna(pd.Series(np.random.choice(fill_list, size=len(df.index))))
        elif option == "C":
            df = df.dropna(subset=null_columns, axis=0)

    return df
