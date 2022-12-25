from lp import PLexer, PParser


def read_file(filename):
    with open(filename, 'r') as file:
        content = file.read()
    return content


def write_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)


def compile_to_masm(filename):
    print(f"Compiling file '{filename}' to MASM32")
    content = read_file(filename)
    lexer = PLexer()
    tokens = lexer.tokenize(content)
    parser = PParser()
    parser.parse(tokens)
    final = parser.cg.dump()
    write_file(f'{filename}.asm', final)
    print(f"Compiled to : '{filename}.asm'")


def main():
    compile_to_masm("xx.yy")


if __name__ == '__main__':
    main()
