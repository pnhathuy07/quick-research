import pandas as pd
from pandas.api.types import is_string_dtype as is_categorical, is_numeric_dtype as is_numerical
from xlsxwriter.utility import xl_range
from functions import err, inp, success, to_front, max_len, validate
import visualization
from configurating import skip_string

import os

directory = os.path.dirname(__file__)


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
    writer_a, filepath_a = setup_writer("analysis", folder, name)
    writer_b, filepath_b = setup_writer("statistics", folder, name)

    # ---------------------------------------- PART B: Survey Analysis ---------------------------------------- #
    # A1: Calculate frequency
    df_all = calculate_frequency(df, noninfo)

    # A2: Write analysis worksheets
    to_excel(df_all, "Tất cả", writer_a, info=info)
    to_excel(df_all[df_all["__Class"].isin(["A", "B", "C"])], "Số đông", writer_a, info=info)
    to_excel(df_all[df_all["__Class"].isin(["D", "E", "F"])], "Số ít", writer_a, info=info)

    # A3: Write grouped analysis worksheets
    while True:
        groups = inp("Which column specifies the groups of the subjects?", default=skip_string)
        if (groups == skip_string) or (groups in df.columns):
            if groups != skip_string:
                df_groups = calculate_frequency(df, noninfo, groups)
                for entry in df_groups[groups].unique():
                    to_excel(df_groups[df_groups[groups] == entry], "(Group) " + entry, writer_a, info=info,
                             title="Group: " + entry, title_size=38)
            break
        err(f"Column '{groups}' does not exist in the list of column names.")

    # ---------------------------------------- PART C: Summary Statistics ---------------------------------------- #
    summary_statistics(df, writer_b, noninfo, groups)

    # ---------------------------------------- PART D: Save and open ---------------------------------------- #
    # D1: Save writers
    writer_a.save()
    writer_b.save()

    success("Excel files successfully saved to this folder.")
    print(folder)

    # D2: Launch Excel
    os.system(f'start "excel.exe" "{filepath_a}"')
    success("Launching Excel...")

    # D3: Avoid leaving the console while launching Excel
    while input() == "":
        pass


# ---------------------------------------- Excel Writer ---------------------------------------- #
def to_excel(df, sheet_name: str, excel_writer, start_row=1, start_col=0, info=None, title=None,
             title_size=58, groups=None, image=None):
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
                                     {"type": "data_bar"})

    # Move selection out of sight
    selection = 10 ** 4
    worksheet.set_selection(selection, selection, selection, selection)


# ---------------------------------------- Survey Analysis ---------------------------------------- #
def calculate_frequency(df, noninfo, groups=skip_string):
    df2 = pd.DataFrame()

    for col in noninfo:
        if groups != skip_string:
            df2.loc[:, col] = df.groupby([groups, col])[col].transform("count")
        else:
            df2.loc[:, col] = df.groupby(col)[col].transform("count")

    df.loc[:, "__Freq"] = df2.sum(axis=1)
    df.sort_values("__Freq", ascending=False, inplace=True)

    if groups != skip_string:
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


def summary_statistics(df, writer_engine, noninfo, groups=skip_string):
    for series in df.columns:
        if series not in ["index", "__Freq", "__Class"]:
            if is_categorical(df[series]):
                if (series in noninfo) or (series in groups):
                    data = categorical_stats(df, series)

                    groups_list = ["Tất cả"]
                    if groups != skip_string:
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
                threshold = 5 * (10 ** 8)  # Avoid recognizing phone numbers as numerical data
                if (df.loc[:, series].mean() < threshold) or (series in noninfo):
                    data = numerical_stats(df, series)

                    if groups != skip_string:
                        for g in df[groups].unique():
                            data = numerical_stats(df[df[groups] == g], series, g, data)

                    data = data.transpose()
                    data = data.reset_index()
                    data.loc[:, "Groups"] = data["index"]
                    data = to_front(data, ["Groups"])
                    data.drop("index", axis=1, inplace=True)

                    to_excel(data, series, writer_engine, title=series, title_size=30, image=[i for i in [
                        visualization.kde(df, series), visualization.kde(df, series, groups)] if i is not None])
