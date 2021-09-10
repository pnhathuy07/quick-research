from functions import success, inp, inp_select, remove_spaces
import re
import pandas as pd
import numpy as np
from scipy import stats

keywords = ("họ và tên", "tên", "tuổi", "số điện thoại", "sđt", "sdt", "dt", "đt", "di động", "mail", "email", "gmail",
            "địa chỉ", "địa chỉ nhà", "thành phố", "quận", "huyện", "phường", "tỉnh", "thành", "lớp", "khối", "trường",
            "là gì", "giới tính", "nghề", "trình độ học vấn", "học vấn")

blacklisted = ("nếu", "sẽ", "làm", "thế nào", "nghĩ", "về việc", "muốn", "thích", "chọn", "chọn một", "nào", "option",
               "có", "không", "có", "không", "theo", "theo bạn", "theo em", "theo anh", "theo chị", "theo anh/chị",
               "theo anh chị", "theo quý", "nhất", "sau đây", "sau", "thấy", "môi trường", "môi")


def column_name_cleaning(df):
    cols = []
    for i in df.columns:
        match = re.findall(r"(?<=\[).+?(?=])", i)
        text = match[-1] if len(match) > 0 else i
        cols.append(" ".join(re.sub(r"[(\[].*?[)\]]", "", text).strip().split()))
    df.columns = cols
    return df


def info_columns(df):
    score = []
    for i, col_name in enumerate(df.columns):
        col_name = remove_spaces(col_name)

        kw_score = sum(remove_spaces(k) in col_name for k in keywords) + 2
        bl_score = sum(remove_spaces(b) in col_name for b in blacklisted) * 10

        score.append((len(col_name) - kw_score * 2 + bl_score) / kw_score + i * 2)

    ls = list(np.array(df.columns)[np.array(score) < 15])
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
                    stats.mode([i for i in df[col] if str(i) != "nan"], axis=None)[0][0])

        # Print rows with missing values (after treatment)
        print(df[null_rows])

    return df
