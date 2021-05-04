class bcol:
    """HEADER, OKBLUE, OKCYAN, OKGREEN, WARNING, FAIL, ENDC, BOLD, UNDERLINE"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

separatorStr = f'{bcol.BOLD}_____________________________________________________________________________________________{bcol.ENDC}'
###
version = '2.3'
productname = f'\n{bcol.BOLD}Quick Research Remastered {bcol.FAIL}[Version {version}]{bcol.ENDC}'
creditLine = f'{productname}\nby Phan Nhat Huy'
###
enter = 'Press Enter to Skip'