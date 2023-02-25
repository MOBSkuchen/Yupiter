import colorama as colora
import sys

colora.Style.UNDERLINE = "\033[4m"

alerts = False
contentLoader = None
contentFile = None
contentOut = None
TrueFile = None
errorDict = {
    1: "NameError",
    2: "ValueError",
    3: "IllegalCharacter",
    4: "SemanticError",
    5: "SyntaxError",
    6: "ImportError",
    7: "OverloadError",
    8: "OptionError"
}


def _errFormat(item, x):
    end = [item.pop(0)]
    for i in item:
        end.append(' ' * x + i)
    return "\n".join(end)


def crit_err(num, name=None, msg=None, cause=None, fix=None):
    """
    Critical errors are errors not triggered by code.
    For example:
        if not os.path.exists(file):
            # The required file could not be found
            xsErrors.crit_err(...)

    :param fix (optional):
    Possible fix
    :param cause:
    Error cause
    :param num:
    Error number
    :param name (optional):
    Error name
    :param msg:
    Show message with it
    :return:
    NULL
    """
    if not name:
        name = errorDict[num]
    print(
        f'{colora.Fore.LIGHTRED_EX}{colora.Style.BRIGHT}{name} {colora.Fore.RESET}: {colora.Fore.RED}{msg}{colora.Fore.RESET}')
    if cause:
        print(f'{colora.Style.BRIGHT}{colora.Fore.RED}This error was caused by{colora.Style.RESET_ALL} : {_errFormat(cause, 27)}')
    if fix:
        print(f'{colora.Style.BRIGHT}{colora.Fore.LIGHTGREEN_EX}This may fix it {colora.Style.RESET_ALL}: {_errFormat(fix, 18)}')
    print(f'{colora.Style.NORMAL}Exited with code {colora.Fore.CYAN}{num}')
    sys.stdout.write(colora.Style.RESET_ALL)
    exit(num)


class STDERR:
    def __init__(self, num, pos: tuple, line, msg, entire):
        self.num = num
        self.pos_start = pos[0]
        self.pos_end = pos[1]
        self.line = line - 1
        self.name = errorDict[num]
        self.msg = msg
        self.entire = entire

    def find(self, entire):
        if self.line != -2:
            ln = contentLoader.splitlines()[self.line]
            offset = len("\n".join(contentLoader.splitlines()[:self.line]))
        else:
            ln = ' N O N E '
            offset = 0
            self.line = 0
        if self.pos_start != -1:
            self.pos_end -= offset
            self.pos_start -= offset + 1
            if self.pos_start == -1:
                self.pos_start = 0
                self.pos_end = 1
        else:
            self.pos_start = 0
            self.pos_end = 0

        if entire:
            self.pos_start = 0
            self.pos_end = len(ln)
        v = ln[:self.pos_start] + '\033[4m' + colora.Style.BRIGHT + ln[
                                                                    self.pos_start:self.pos_end] + '\033[0m' + colora.Fore.LIGHTYELLOW_EX + ln[
                                                                                                                                            self.pos_end:]
        return f'>   {colora.Fore.LIGHTYELLOW_EX}{v}'

    def trigger(self):
        print(
            f'In "{colora.Fore.BLUE}{contentFile}{colora.Fore.RESET}" at line {colora.Fore.CYAN}{self.line}{colora.Fore.RESET}:')
        print(self.find(self.entire))
        print(
            f'{colora.Fore.LIGHTRED_EX}{self.name}{colora.Fore.RESET} [{colora.Fore.CYAN}{self.num}{colora.Fore.RESET}] | {colora.Fore.RED}{self.msg}{colora.Fore.RESET}')
        raise Exception()


def stderr(num, pos: tuple, line, msg, entire=False):
    err = STDERR(num, pos, line, msg, entire)
    err.trigger()


def stdwarning(msg):
    if alerts:
        print(f'{colora.Fore.LIGHTYELLOW_EX}WARNING{colora.Fore.RESET} : {colora.Fore.MAGENTA}{msg}{colora.Fore.RESET}')
