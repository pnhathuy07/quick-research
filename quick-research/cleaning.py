from functions import remove_spaces, success, inp, inp_select
import re
import pandas as pd
import numpy as np
from scipy import stats

keywords = ("name", "họ và tên", "tên", "full name", "first name", "last name", "surname", "tuổi", "age", "how old",
            "phone", "số điện thoại", "sđt", "sdt", "dt", "đt", "mobile", "di động", "mail", "email", "gmail",
            "địa chỉ", "địa chỉ nhà", "address", "thành phố", "quận", "huyện", "phường", "tỉnh", "thành", "city",
            "province", "district", "lớp", "khối", "class", "grade", "trường", "school", "là gì", "giới tính", "gender",
            "sex", "nghề", "job", "career", "trình độ học vấn", "education", "học vấn")

blacklisted_words = ("nếu", "sẽ", "làm", "thế nào", "if", "how would", "how do", "think", "nghĩ", "về việc", "muốn",
                     "want", "thích", "interested", "like", "prefer", "would you", "rather", "chọn", "choose", "pick",
                     "nào", "option", "following", "có", "không", "có", "không", "theo", "theo bạn", "theo em",
                     "theo anh", "theo chị", "theo anh/chị", "theo anh chị", "opinion", "best", "nhất", "sau đây",
                     "sau")


def to_score(word):
    """Artificial learning model."""
    word = remove_spaces(word.lower())

    return (
               (
                       len(word)
                       - sum(len(k) for k in keywords if remove_spaces(k) in word)
                       + sum(remove_spaces(b) in word for b in blacklisted_words) * 8
               )
           ) / (0.2 + sum(remove_spaces(k) in word for k in keywords))


def column_name_cleaning(df):
    cols = []
    parenthesis = r"[(\[].*?[)\]]"
    for i in df.columns:
        match = re.findall(r"(?<=\[).+?(?=])", i)
        text = match[-1] if len(match) > 0 else i
        cols.append(" ".join(re.sub(parenthesis, "", text).strip().split()))
    df.columns = cols
    return df


def info_extract(df):
    ls = np.array(df.columns)
    ls_mp = np.array(list(map(lambda x: to_score(x), ls)))

    ls = list(ls[ls_mp < 16])
    success(f"We have recognized that the following columns contain personal information of the subjects\n{ls}")

    confirm = inp("Is this recognition correct?", "Yes", "No", default="A")
    if confirm != "A":
        ls = inp_select("Which column do you want to add or remove?", df.columns.tolist(), current_list=ls,
                        n_max=len(df.columns) - 1)
        success(f"Here are your info columns again\n{ls}")

    return ls


def clean_na(df: any, noninfo: list):
    """Handle missing values."""
    has_null = False
    null_columns = []
    for i in list(noninfo):
        if df[i].isnull().values.any():
            has_null = True
            null_columns.append(i)

    if has_null:
        # Print rows with missing values
        null_rows = df.isnull().any(axis=1)
        print(df[null_rows])

        option = inp(
            "There are missing values in your data. How do you want to deal with these missing values?",
            "Remove rows with missing values", "Assign random values", "Mode imputation", "Leave blank", default="A")

        if option == "A":
            # Remove rows with missing values
            df = df.dropna(subset=null_columns, axis=0)
        elif option == "B":
            # Assign random values
            for col in null_columns:
                fill_list = [i for i in df[col] if str(i) != "nan"]
                df.loc[:, col] = df[col].fillna(pd.Series(np.random.choice(fill_list, size=len(df.index))))
        elif option == "C":
            # Mode imputation
            for col in null_columns:
                df.loc[:, col] = df[col].fillna(
                    stats.mode([i for i in df[col] if not str(i) == "nan"], axis=None)[0][0])

        # Print rows with missing values (after treatment)
        print(df[null_rows])

    return df
