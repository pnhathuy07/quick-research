class ConsoleColors:
    header = "\033[95m"
    blue = "\033[94m"
    cyan = "\033[96m"
    green = "\033[92m"
    warning = "\033[93m"
    red = "\033[91m"
    end = "\033[0m"
    bold = "\033[1m"
    underline = "\033[4m"


separator_string = f"{ConsoleColors.bold}-------------------------------------------" \
                   f"--------------------------------------------{ConsoleColors.end}"

version = "3.0"
product_name = f"\n{ConsoleColors.bold}Quick Research {ConsoleColors.blue}(Version {version})" \
               f"{ConsoleColors.end}"
creditLine = f"{product_name}\nPhan Nhat Huy"

skip_string = "Press Enter to Skip"
