import os
import configurations


def credit():
    """Print the credit line (i.e. name, version, creator)"""
    print(configurations.creditLine)
    print(configurations.separator_string)


directory = os.path.dirname(__file__)
logo_directory = [directory + "/source/images/transparent/colorful/black_text/logo_horizontal.png",
                  directory + "/source/images/transparent/colorful/logo.png"]


def page(excel_writer):
    sheet_name = "Quick Research"

    workbook = excel_writer.book
    worksheet = workbook.add_worksheet(sheet_name)

    # White background
    title_format = workbook.add_format({"fg_color": "#ffffff"})
    worksheet.conditional_format(0, 0, 100, 100,
                                 {"type": "no_errors", "format": title_format})

    # Hide rows
    worksheet.set_default_row(hide_unused_rows=True)
    worksheet.set_row(0, 409)

    # Hide columns
    worksheet.set_column("B:XFD", None, None, {"hidden": True})
    worksheet.set_column(0, 0, 137)

    # Logo
    worksheet.insert_image(0, 0, logo_directory[0], dict(x_offset=0, y_offset=0, x_scale=.5, y_scale=.5))

    # Move selection out of sight
    selection_a, selection_b = 270206, 11187
    worksheet.set_selection(selection_a, selection_b, selection_a, selection_b)
