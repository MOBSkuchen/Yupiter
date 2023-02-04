import colorama as colora
import sys

alerts = False
contentLoader = None
contentFile = None
errorDict = {
    1: "NameError",
    2: "ValueError",
    3: "IllegalCharacter",
    4: "SemanticError",
    5: "SyntaxError",
    6: "ImportError"
}


def F_error(num, name, msg, trigger=True):
    print(
        f'{colora.Fore.LIGHTRED_EX}{colora.Style.BRIGHT}{name} {colora.Fore.RESET}: {colora.Fore.RED}{msg}{colora.Fore.RESET}')
    print(f'{colora.Style.NORMAL}Exited with code {colora.Fore.CYAN}{num}')
    sys.stdout.write(colora.Style.RESET_ALL)
    if trigger:
        exit(num)


class STDERR:
    def __init__(self, num, pos: tuple, line, msg, entire):
        self.num = num
        self.pos_start = pos[0]
        self.pos_end   = pos[1]
        self.line = line - 1
        self.name = errorDict[num]
        self.msg = msg
        self.entire = entire

    def find(self, entire):
        if self.line != -2:
            ln = contentLoader.splitlines()[self.line]
            offset = len("\n".join(contentLoader.splitlines()[:self.line]))
        else:
            ln = ' / N O N E \ '
            offset = 0
            self.line = 0
        if self.pos_start != -1:
            self.pos_start -= offset - 4
            self.pos_end -= offset + self.pos_start - 5
        else:
            self.pos_start = 0
            self.pos_end = 0

        if entire:
            self.pos_start = 4
            self.pos_end = len(ln)
        return f'>   {colora.Fore.LIGHTYELLOW_EX}{ln}{colora.Fore.RESET}\n{" " * self.pos_start}{colora.Fore.MAGENTA}{"^" * self.pos_end}{colora.Fore.RESET}'

    def trigger(self):
        print(f'In "{colora.Fore.BLUE}{contentFile}{colora.Fore.RESET}" at line {colora.Fore.CYAN}{self.line}{colora.Fore.RESET}:')
        print(self.find(self.entire))
        print(f'{colora.Fore.LIGHTRED_EX}{self.name}{colora.Fore.RESET} [{colora.Fore.CYAN}{self.num}{colora.Fore.RESET}] | {colora.Fore.RED}{self.msg}{colora.Fore.RESET}')
        raise Exception()


def stderr(num, pos: tuple, line, msg, entire=False):
    err = STDERR(num, pos, line, msg, entire)
    err.trigger()


def stdwarning(msg):
    if alerts:
        print(f'{colora.Fore.LIGHTYELLOW_EX}WARNING{colora.Fore.RESET} : {colora.Fore.MAGENTA}{msg}{colora.Fore.RESET}')
