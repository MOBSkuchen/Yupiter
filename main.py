import os
import sys
import colorama as colora
from errors import crit_err as error
import errors as xsErrors
from compiler import Compiler
from interpreter import Interpreter
from lp import PLexer, PParser
from syntax_higlighting import light

__version__ = '0.6'
colora.Style.UNDERLINE = "\033[4m"

long_opts = {
    "--noalert": 'noalert',
    "--x32": "32bit",
    "--alert": "alert",
    "--view": "view",
    "--compile": "compile",
    "--run": "run"
}
short_opts = {
    "-n": "--noalert",
    "-x": "--x32",
    "-a": "--alert",
    "-v": "--view",
    "-c": "--compile",
    "-r": "--run"
}
inf_long_opts = {
    "--help": "help",
    "--version": "version"
}
inf_short_opts = {
    "-h": "--help",
    "-v": "--version"
}

opt_doc = {
    "noalert": "Disable warnings",
    "32bit": "Compile using 32bit registers (compilation only)",
    "alert": "Enable warnings",
    "view": "View using syntax highlighting",
    "compile": "Compile",
    "run": "Run (interpretation mode)",
    "version": f"Get {colora.Fore.BLUE}{colora.Style.BRIGHT}Yupiter{colora.Style.RESET_ALL} version",
    "help": "Get this help page"
}


def version_func():
    print(f'{colora.Fore.BLUE}{colora.Style.BRIGHT}Yupiter{colora.Style.RESET_ALL} {colora.Fore.YELLOW}V{colora.Fore.RESET}{colora.Fore.GREEN}{__version__}{colora.Fore.RESET}')


def help_func():
    version_func()
    print(f'Usage : {colora.Fore.BLUE}{colora.Style.BRIGHT}Yupiter{colora.Style.RESET_ALL} <(optional) file> <options>')
    print(f"[The file must end with '.yp']")
    print(f'  {colora.Fore.CYAN}{colora.Style.UNDERLINE}Runtime-Options{colora.Style.RESET_ALL}:')
    for opt in short_opts:
        lopt = short_opts[opt]
        print(f'    {lopt} / {opt} : {opt_doc[long_opts[lopt]]}')
    print(f' {colora.Fore.CYAN}{colora.Style.UNDERLINE}Other options{colora.Style.RESET_ALL}:')
    for opt in inf_short_opts:
        lopt = inf_short_opts[opt]
        print(f'    {lopt} / {opt} : {opt_doc[inf_long_opts[lopt]]}')


def gather_options(args):
    options = []
    for arg in args:
        if arg in long_opts.keys():
            options.append(long_opts[arg])
        elif arg in short_opts.keys():
            options.append(long_opts[short_opts[arg]])
        else:
            error(8, 'OptionError', f'Invalid option', cause=[f"You passed in an invalid option : ", arg], fix=["Input a valid option"])
    return options


def read(target):
    with open(target, 'r') as file:
        content = file.read()
    xsErrors.contentLoader = content
    xsErrors.contentFile = fmt_file(target)
    xsErrors.TrueFile = target
    xsErrors.contentOut = xsErrors.TrueFile[:len(xsErrors.TrueFile) - 3] + '.asm'
    return content


def write(target, content):
    with open(target, 'w') as file:
        file.write(content)


def fmt_file(file):
    file = os.path.abspath(file).replace('\\', '/')
    if len(file) < 10:
        return file
    return file.split('/')[0] + '/.../' + file.split('/')[file.count('/')]


def lp(content):
    lexer = PLexer()
    tokens = lexer.tokenize(content)
    parser = PParser()
    parser.parse(tokens)
    return parser.ast


def compile_(opts, ast):
    print(
        f'{colora.Fore.LIGHTYELLOW_EX}Compiling {colora.Fore.RESET}{colora.Fore.BLUE}{colora.Style.BRIGHT}{xsErrors.contentFile}'
        f'{colora.Style.RESET_ALL}{colora.Fore.LIGHTYELLOW_EX} to{colora.Fore.BLUE}{colora.Style.BRIGHT} '
        f'{fmt_file(xsErrors.contentOut)}{colora.Style.RESET_ALL}'
        f'{colora.Fore.LIGHTYELLOW_EX} with options{colora.Fore.RESET}: '
        f'{colora.Fore.MAGENTA}{f"{colora.Fore.RESET}, {colora.Fore.MAGENTA}".join(opts)}')
    print()
    sys.stdout.write(colora.Style.RESET_ALL)
    compiler = Compiler(opts)
    out = compiler.make(ast)
    write(xsErrors.contentOut, out)


def run(opts, ast):
    print(
        f'{colora.Fore.LIGHTYELLOW_EX}Running {colora.Fore.RESET}{colora.Fore.BLUE}{colora.Style.BRIGHT}{xsErrors.contentFile}'
        f'{colora.Style.RESET_ALL}{colora.Fore.LIGHTYELLOW_EX} to{colora.Fore.BLUE}{colora.Style.BRIGHT} '
        f'{fmt_file(xsErrors.contentOut)}{colora.Style.RESET_ALL}'
        f'{colora.Fore.LIGHTYELLOW_EX} with options{colora.Fore.RESET}: '
        f'{colora.Fore.MAGENTA}{f"{colora.Fore.RESET}, {colora.Fore.MAGENTA}".join(opts)}')
    if "32bit" in opts:
        xsErrors.stdwarning(f'32bit option has no effect in interpretation (run) mode')
    print()
    sys.stdout.write(colora.Style.RESET_ALL)
    interpreter = Interpreter(opts)
    out = interpreter.make(ast)


def inf_opts_con(cmd):
    match cmd:
        case "help":
            help_func()
        case "version":
            version_func()


def main():
    args = sys.argv
    args.pop(0)
    if not len(args) > 0:
        return
    target = args.pop(0)
    if (target.startswith('--') and target in inf_long_opts) or (target.startswith('-') and target in inf_short_opts):
        if target.startswith('--'):
            target = inf_long_opts[target]
        else:
            target = inf_long_opts[inf_short_opts[target]]
        inf_opts_con(target)
        return
    if not target.endswith('.yp'):
        error(4, 'FileType', 'Invalid FileType (must be .yp)')
    if not os.path.exists(target):
        error(2, 'FileNotFound', f'The input file could not be found', cause=[f"File not found '{target}'"], fix=["Input an existing file"])
    opts = gather_options(args)
    if "32bit" not in opts:
        opts.append('64bit')
    if "alert" not in opts and "noalert" not in opts:
        opts.append('noalert')
    if "alert" in opts:
        xsErrors.alerts = True
    v = read(target)
    target = xsErrors.contentFile
    if "view" in opts:
        print(
            f'{colora.Fore.LIGHTYELLOW_EX}Viewing {colora.Fore.RESET}{colora.Fore.BLUE}{colora.Style.BRIGHT}{target}'
            f'{colora.Style.RESET_ALL}:')
        if not os.path.exists('syntax.json'):
            xsErrors.crit_err(6,  f"The library 'syntax.json' could not be found",
                              cause=['Trying to view code without the syntax library'], fix=['Try reinstalling Yupiter', "Download the 'syntax.json' library"])
        print(light(v, 'syntax.json'))
        print()
    ast = lp(v)
    if "build" in opts:
        compile_(opts, ast)
    elif "run" in opts:
        run(opts, ast)
    else:
        pass


if __name__ == '__main__':
    abnormal = False
    try:
        main()
    except Exception as ex:
        if not ex.__class__ == Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f'{colora.Style.UNDERLINE}Internal error, please open an issue with the following traceback{colora.Style.RESET_ALL} :\nIn {filename} at line {exc_tb.tb_lineno}: \n{ex.with_traceback(None)}')
            print('-' * 20)
        print(f'Completed {colora.Fore.RED}abnormally')
        abnormal = True

    if not abnormal:
        print(f'Completed {colora.Fore.LIGHTYELLOW_EX}successfully')
    sys.stdout.write(colora.Style.RESET_ALL)
