import pandas as pd
import numpy as np
from pandas.api.types import is_string_dtype as is_categorical, is_numeric_dtype as is_numerical
import xlsxwriter
from xlsxwriter.utility import xl_range
from functions import err, inp_select, success, to_front, max_len, validate
import visualization
import branding

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.pipeline import make_pipeline

import os

directory = os.path.dirname(__file__)
logo_directory = [directory + "/source/images/transparent/colorful/black_text/logo_horizontal.png"]


def setup_writer(workbook_name, folder, filename) -> tuple:
    success("Setting up writer...")
    filepath = "{}\\{}_{}.xlsx".format(folder, filename, workbook_name)
    print(filepath)

    excel_writer = pd.ExcelWriter(filepath, engine="xlsxwriter")
    return excel_writer, filepath


# ---------------------------------------- Main ---------------------------------------- #
def main(df, info, noninfo, folder, name):
    pd.options.mode.chained_assignment = None

    # ---------------------------------------- PART A: Setup writers ---------------------------------------- #
    # A1: Setup writers
    writer_a, filepath_a = setup_writer("analysis", folder, name)
    writer_b, filepath_b = setup_writer("statistics", folder, name)

    # A2: Branding
    branding.page(writer_a)
    branding.page(writer_b)

    # ---------------------------------------- PART B: Survey Analysis ---------------------------------------- #
    # B1: Calculate frequency
    df_all = cluster_by_features(df, noninfo)
    df_all = calculate_frequency(df_all, noninfo)

    # B2: Write analysis worksheets
    to_excel(df_all, "Tất cả", writer_a, info=info, image=logo_directory)
    to_excel(df_all[df_all["__Class"].isin(["A", "B", "C"])], "Số đông", writer_a, info=info, image=logo_directory)
    to_excel(df_all[df_all["__Class"].isin(["D", "E", "F"])], "Số ít", writer_a, info=info, image=logo_directory)

    # B3: Write grouped analysis worksheets
    groups = inp_select("Which column specifies the groups of the subjects?", df.columns.tolist(), n_max=1)
    if len(groups) > 0:
        groups = groups[0]
        df_groups = calculate_frequency(df, noninfo, groups)
        for entry in df_groups[groups].unique():
            to_excel(df_groups[df_groups[groups] == entry], "(Group) " + entry, writer_a, info=info,
                     title="Group: " + entry, title_size=42)
    else:
        groups = None

    # ---------------------------------------- PART C: Summary Statistics ---------------------------------------- #
    success("Creating Summary Statistics.")
    summary_statistics(df, writer_b, noninfo, groups)

    # ---------------------------------------- PART D: Save and open ---------------------------------------- #
    # D1: Save writers
    success("Saving files...")

    has_error = True
    while has_error:
        try:
            writer_a.save()
            writer_b.save()
            has_error = False
        except xlsxwriter.exceptions.FileCreateError:
            err("Please save your work and close Excel to save new files.")
            input("Press Enter to Continue.\n")

    success("Excel files successfully saved to this folder.")
    print(folder)

    # D2: Launch Excel
    os.system(f'start "excel.exe" "{filepath_a}"')
    success("Launching Excel...")

    # D3: Avoid exiting the console while launching Excel
    while input() == "":
        pass


# ---------------------------------------- Excel Writer ---------------------------------------- #
def to_excel(df, sheet_name: str, excel_writer, start_row=1, start_col=0, info=None, title=None,
             title_size=62, groups=None, image=None):
    if groups is None:
        groups = list()

    df.drop("index", axis=1, errors="ignore", inplace=True)
    if title is None:
        title = sheet_name

    sheet_name = validate(sheet_name)
    sheet_name = max_len(sheet_name)

    df.to_excel(excel_writer, sheet_name=sheet_name, index=False, startrow=start_row, startcol=start_col)

    workbook = excel_writer.book
    worksheet = excel_writer.sheets[sheet_name]

    max_row, max_col = df.shape

    # Add a filter
    worksheet.autofilter(start_row, start_col, start_row + max_row, start_col + max_col - 1)
    worksheet.set_row(start_row, 30)

    # Personal information format
    info_format = workbook.add_format({"color": "#0955ec"})

    if info is not None:
        for col in info:
            loc = df.columns.get_loc(col)
            worksheet.conditional_format(start_row + 1, start_col + loc, start_row + max_row + 1, start_col + loc,
                                         {"type": "no_errors", "format": info_format})

    # Percentage format
    percentage_format = workbook.add_format({"num_format": "0%"})
    if "Percentage" in df.columns:
        loc = df.columns.get_loc("Percentage")
        worksheet.conditional_format(start_row + 1, start_col + loc, start_row + max_row + 1, start_col + loc,
                                     {"type": "no_errors", "format": percentage_format})

    # Fit column width
    for idx, col_name in enumerate(df.columns.values):
        series = df.loc[:, col_name]
        column_length = max((
            series.astype(str).map(len).max(),  # Length of largest item
            len(str(series.name))  # Length of column name/header
        )) + 2  # Adding extra space
        worksheet.set_column(start_col + idx, start_col + idx, column_length)

    # Worksheet Title
    title_format = workbook.add_format({"bold": True, "font_size": title_size, "fg_color": "#ffffff"})
    worksheet.conditional_format(start_row - 1, start_col, start_row - 1, start_col + max_col - 1,
                                 {"type": "no_errors", "format": title_format})
    worksheet.write(start_row - 1, start_col, title, title_format)

    # Graph
    if image is not None:
        offset = 0
        for i in image:
            worksheet.insert_image(start_row + max_row + 1, start_col, i, {"x_offset": offset, "y_offset": 2})
            offset += 614

    # Thick borders
    b_border = workbook.add_format(
        {
            "bottom": 1,
            "color": "#000000"
        }
    )
    header_format = workbook.add_format(
        {
            "top": 1,
            "bottom": 2,
            "color": "#000000"
        }
    )
    l_thick_border = workbook.add_format(
        {
            "left": 2,
            "color": "#000000"
        }
    )

    for i in last_rows_in_group(df, "__Class"):
        worksheet.conditional_format(
            xl_range(start_row + i + 1, start_col, start_row + i + 1, start_col + max_col - 1),
            {"type": "no_errors", "format": b_border})

    worksheet.conditional_format(xl_range(start_row, start_col, start_row, start_col + max_col - 1),
                                 {"type": "no_errors", "format": header_format})
    worksheet.conditional_format(
        xl_range(start_row - 1, start_col + max_col, start_row + max_row, start_col + max_col),
        {"type": "no_errors", "format": l_thick_border})

    if "__Freq" in df.columns:
        loc = df.columns.get_loc("__Freq")
        worksheet.conditional_format(start_row + 1, start_col + loc, start_row + max_row + 1, start_col + loc,
                                     {"type": "3_color_scale"})
    for i in groups:
        loc = df.columns.get_loc(i)
        worksheet.conditional_format(start_row + 1, start_col + loc, start_row + max_row + 1, start_col + loc,
                                     {"type": "data_bar", "bar_color": "#ffb628"})

    # Move selection out of sight
    selection_a, selection_b = 270206, 11187
    worksheet.set_selection(selection_a, selection_b, selection_a, selection_b)


# ---------------------------------------- Survey Analysis ---------------------------------------- #
def cluster_by_features(df, noninfo):
    n_clusters = len(df.index) // 6 + 1

    X = pd.get_dummies(df.loc[:, noninfo], drop_first=True)

    pipe = make_pipeline(StandardScaler(), KMeans(n_clusters=n_clusters))
    labels = pipe.fit_predict(X)

    df2 = df.copy()
    df2.loc[:, "__Cluster"] = np.core.defchararray.add("Group ", (np.array(labels) + 1).astype(str))
    df2 = to_front(df2, ["__Cluster"])

    return df2


def calculate_frequency(df, noninfo, groups=None):
    df2 = pd.DataFrame()

    for col in noninfo:
        if groups is not None:
            df2.loc[:, col] = df.groupby([groups, col])[col].transform("count")
        else:
            df2.loc[:, col] = df.groupby(col)[col].transform("count")

    df.loc[:, "__Freq"] = df2.sum(axis=1)
    df.sort_values("__Freq", ascending=False, inplace=True)

    if groups is not None:
        for g in df[groups].unique():
            df.loc[df[groups] == g, :] = cluster_by_frequency(df[df[groups] == g])
    else:
        df = cluster_by_frequency(df)

    df = to_front(df, ["__Freq", "__Class"])
    return df


def cluster_by_frequency(df):
    df.loc[:, "__Class"] = pd.cut(df["__Freq"], bins=6, labels=["F", "E", "D", "C", "B", "A"])
    return df


def last_rows_in_group(df, col):
    df = df.reset_index()
    if "__Class" in df.columns:

        df = df[~df.duplicated(subset=col, keep="last")]
    else:
        df = df.iloc[[-1]]
    return df.index.tolist()


# ---------------------------------------- Summary Statistics ---------------------------------------- #
def categorical_stats(df, series, group_by="Tất cả"):
    data = pd.DataFrame(df[series].value_counts().reset_index())
    data.loc[:, "Values"] = data["index"]
    data.loc[:, group_by] = data[series]
    data.drop([series], axis=1, errors="ignore", inplace=True)
    data = data.set_index("index")
    return data


def numerical_stats(df, series, group_by="Tất cả", old_data=None):
    if old_data is None:
        old_data = list()
    data = pd.DataFrame(old_data)
    data.loc[:, group_by] = df[series].agg(["sum", "count", "mean", "median", "min", "max", "std"])
    return data


def summary_statistics(df, writer_engine, noninfo, groups):
    for series in df.columns:
        if series not in ["index", "__Freq", "__Class", "__Cluster"]:
            if is_categorical(df[series]):
                if (series in noninfo) or (series == groups):
                    data = categorical_stats(df, series)

                    groups_list = ["Tất cả"]
                    if groups is not None:
                        for g in df[groups].unique():
                            data.loc[:, g] = 0
                            data_grouped = categorical_stats(df[df[groups] == g], series, g)
                            data.update(data_grouped)

                        groups_list += list(df[groups].unique())

                        data2 = data.set_index("Values").iloc[:, 1:]
                    else:
                        data2 = data.set_index("Values")

                    to_excel(data, series, writer_engine, title=series, title_size=30, groups=groups_list,
                             image=[visualization.pie(data, "Values", "Tất cả", series),
                                    visualization.bar(data2, series)])
            elif is_numerical(df[series]):
                threshold = 1 * (10 ** 8)  # Avoid recognizing phone numbers as numerical data
                if (df.loc[:, series].mean() < threshold) or (series in noninfo):
                    data = numerical_stats(df, series)

                    if groups is not None:
                        for g in df[groups].unique():
                            data = numerical_stats(df[df[groups] == g], series, g, data)

                    data = data.transpose()
                    data = data.reset_index()
                    data.loc[:, "Groups"] = data["index"]
                    data = to_front(data, ["Groups"])
                    data.drop("index", axis=1, inplace=True)

                    to_excel(data, series, writer_engine, title=series, title_size=30, image=[i for i in [
                        visualization.kde(df, series), visualization.kde(df, series, groups)] if i is not None])
