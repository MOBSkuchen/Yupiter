import os
import sys
import colorama as colora
from errors import F_error as error
import errors as xsErrors
from compiler import PLexer, PParser, Compiler


long_opts = {
    "--noalert": 'noalert',
    "--x32": "32bit",
    "--alert": "alert"
}
short_opts = {
    "-n": "--noalert",
    "-x": "--x32",
    "-a": "--alert"
}


def gather_options(args):
    options = []
    for arg in args:
        if arg in long_opts.keys():
            options.append(long_opts[arg])
        elif arg in short_opts.keys():
            options.append(long_opts[short_opts[arg]])
        else:
            error(3, 'OptionError', f'Invalid option')
    return options


def read(target):
    with open(target, 'r') as file:
        content = file.read()
    xsErrors.contentLoader = content
    xsErrors.contentFile   = target
    return content


def write(target, content):
    with open(target, 'w') as file:
        file.write(content)


def start(opts, content):
    lexer = PLexer()
    tokens = lexer.tokenize(content)
    parser = PParser()
    parser.parse(tokens)
    compiler = Compiler(opts)
    out = compiler.make(parser.ast)
    write('main.asm', out)


def main():
    args = sys.argv
    args.pop(0)
    if not len(args) > 0:
        error(1, 'ArgumentError', f'Too few arguments')
    target = args.pop(0)
    if not target.endswith('.yp'):
        error(4, 'FileType', 'Invalid FileType (must be .yp)')
    if not os.path.exists(target):
        error(2, 'FileNotFound', f'The input file could not be found')
    opts = gather_options(args)
    if "32bit" not in opts:
        opts.append('64bit')
    if "alert" not in opts and "noalert" not in opts:
        opts.append('noalert')
    if "alert" in opts:
        xsErrors.alerts = True
    print(f'{colora.Fore.LIGHTYELLOW_EX}Compiling {colora.Fore.RESET}{colora.Fore.BLUE}{colora.Style.BRIGHT}{target}{colora.Style.RESET_ALL}{colora.Fore.LIGHTYELLOW_EX} with options{colora.Fore.RESET}: {colora.Fore.MAGENTA}{f"{colora.Fore.RESET}, {colora.Fore.MAGENTA}".join(opts)}')
    print()
    sys.stdout.write(colora.Style.RESET_ALL)
    start(opts, read(target))


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        raise ex
        pass
    sys.stdout.write(colora.Style.RESET_ALL)
