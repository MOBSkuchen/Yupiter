from errors import InstructionError

loc_table = {
    "include": "\masm32\include\{inc}.inc",
    "include_lib": "\masm32\lib\{lib}.lib",
    "import": "\masm32\cora\{mod}.inc"
}
func_table = {
    "invoke": "invoke {method}, {args}",
    "include": "include {pos}",
    "include_lib": "includelib {pos}",
    "move": "mov {dst}, {src}",
    "func_def": "{name} proto {args}",
    "return": "ret",
    "func_dec": "{name} proc {args}",
    "func_end": "ret\n{name} endp",
    "var_assign": "{name} {x} {value}, 0"
}
lits = {
    "print": "Print",
    "exit": "Exit",
    "input": "Input"
}


class Variables:
    variables = {}
    emg = None
    c = 0
    c2 = -1

    @staticmethod
    def assign(name, func=False):
        if name in Variables.variables.keys():
            Variables.emg = Variables.variables[name]
        else:
            Variables.emg = None
        Variables.variables[name] = f'{"F" if func else "v"}_{Variables.c}'
        Variables.c += 1
        return Variables.variables[name]

    @staticmethod
    def location():
        Variables.c2 += 1
        return f'l_{Variables.c2}'

    @staticmethod
    def register():
        for lit in lits.keys():
            lg = lits[lit]
            Variables.variables[lit] = lg


class Codes:
    @staticmethod
    def invoke(method, args):
        return func_table['invoke'].format(method=method, args=args)

    @staticmethod
    def include(inc):
        return func_table['include'].format(pos=loc_table['include'].format(inc=inc))

    @staticmethod
    def include_lib(lib):
        return func_table['include_lib'].format(pos=loc_table['include_lib'].format(lib=lib))

    @staticmethod
    def move(dst, src):
        return func_table['move'].format(dst=dst, src=src)

    @staticmethod
    def define_function(name, arg_num):
        x = []
        for i in range(arg_num):
            x.append(":dword")
        return func_table['func_def'].format(name=name, args=",".join(x))

    @staticmethod
    def var_clear(name):
        return Codes.move(name, "NULL")

    @staticmethod
    def ret():
        return func_table['return']

    @staticmethod
    def import_(name):
        return func_table["include"].format(pos=loc_table["import"].format(mod=name))

    @staticmethod
    def declare_function(name, args):
        x = []
        for arg in args:
            x.append(f'{arg}:dword')
        return func_table['func_dec'].format(name=name, args=",".join(x))

    @staticmethod
    def end_func(name):
        return func_table["func_end"].format(name=name)

    @staticmethod
    def var_assign(name, value, string=False):
        return func_table["var_assign"].format(x='db' if string else 'dword', name=name, value=value)

    @staticmethod
    def start_begin():
        return 'start:'

    @staticmethod
    def loc_begin(name):
        return f'{name}:'

    @staticmethod
    def start_end():
        return 'end start'

    @staticmethod
    def operation(op, lhs, rhs):
        return f'{op} {lhs}, {rhs}'

    @staticmethod
    def compare(lhs, rhs):
        return Codes.operation('cmp', lhs, rhs)

    @staticmethod
    def add(lhs, rhs):
        return Codes.operation('add', lhs, rhs)

    @staticmethod
    def mul(lhs, rhs):
        return Codes.operation('mul', lhs, rhs)

    @staticmethod
    def div(lhs, rhs):
        return Codes.operation('div', lhs, rhs)

    @staticmethod
    def sub(lhs, rhs):
        return Codes.operation('sub', lhs, rhs)

    @staticmethod
    def if_(operation):
        return f'.if {operation}'

    @staticmethod
    def elif_(operation):
        return f'.elseif {operation}'

    @staticmethod
    def else_():
        return '.else'

    @staticmethod
    def if_close():
        return '.endif'

    @staticmethod
    def jump(loc):
        return f'jmp {loc}'

    @staticmethod
    def cond_jump(loc, op):
        match op:
            case "==":
                return f'je {loc}'
            case "!=":
                return f'jne {loc}'
            case ">":
                return f'jg {loc}'
            case "<":
                return f'jl {loc}'
            case _:
                raise InstructionError(f"The instruction '{op}' was not found!")


heap_reg = []


class Codegen:
    data = [".data"]
    code = [".code"]
    head = [".386", ".model flat, stdcall", "option casemap: none"]
    segments = {
        "start": []
    }
    pkgs = []
    cur = segments["start"]

    def __init__(self):
        self.if_ret = None
        self.prev = None
        Variables.register()

    def set_cur(self, name):
        self.cur = self.segments[name]

    def include(self, file):
        if file in self.pkgs:
            return
        self.pkgs.append(file)
        self.head.append(Codes.include(file))

    def include_lib(self, file):
        if file in self.pkgs:
            return
        self.pkgs.append(file)
        self.head.append(Codes.include_lib(file))

    def import_(self, file):
        if file in self.pkgs:
            compiler_warning(f"Double import ({file})")
            return
        self.pkgs.append(file)
        self.head.append(Codes.import_(file))

    def translate_operation(self, lhs, rhs, op):
        self.cur.append(Codes.move('eax', lhs))
        self.cur.append(Codes.move('ebx', rhs))
        match op:
            case '+':
                self.cur.append(Codes.operation('add', 'eax', 'ebx'))
                self.cur.append(Codes.move(lhs, 'eax'))
            case '-':
                self.cur.append(Codes.operation('sub', 'eax', 'ebx'))
                self.cur.append(Codes.move(lhs, 'eax'))
            case 'c':
                self.cur.append(Codes.operation('cmp', 'eax', 'ebx'))
            case '*':
                self.cur.append(Codes.operation('imul', 'eax', 'ebx'))
                self.cur.append(Codes.move(lhs, 'eax'))
            case '/':
                self.cur.append(Codes.operation('idiv', 'eax', 'ebx'))
                self.cur.append(Codes.move(lhs, 'eax'))

    def new_segment(self):
        name = Variables.location()
        self.segments[name] = []
        return name

    def handle_expr(self, expr):
        return expr

    def if_(self, expr):
        r, op, l = self.handle_expr(expr)
        self.cur.append(Codes.move('ecx', r))
        self.cur.append(Codes.compare(l, 'ecx'))
        self.prev = self.cur
        name = self.new_segment()
        self.cur.append(Codes.cond_jump(name, op))
        self.set_cur(name)

    def else_if(self):
        if self.prev:
            self.cur = self.prev
        name = self.new_segment()
        self.cur.append(Codes.jump(name))
        self.set_cur(name)

    def closeif(self):
        name = self.new_segment() if not self.if_ret else self.if_ret
        self.cur.append(Codes.jump(name))
        self.if_ret = name

    def endif(self):
        self.set_cur(self.if_ret)
        self.if_ret = None
        self.prev = None

    def call(self, name, args):
        argx = []
        for arg in args:
            if type(arg) == int:
                argx.append(arg)
        self.cur.append(Codes.invoke(name, " ".join(args)))

    def var_assign(self, name, value):
        name = Variables.assign(name)
        if type(value) == int or value.isnumeric():
            ext = 'dword'
        else:
            ext = 'db'
        self.data.append(f'{name} {ext} {value}')

    def dump(self):
        code = ['.code']
        start = ['start:'] + self.segments.pop('start')
        for segment in self.segments.keys():
            value = self.segments[segment]
            value = [f'{segment}:'] + value + ['ret']
            code = code + value
        full = self.head + self.data + code + start
        full = "\n".join(full)
        return full


def compiler_warning(message):
    print(f'COMPILER WARNING : {message}')


def main():
    cg = Codegen()
    cg.import_('stdlib')
    cg.var_assign('a', 10)
    cg.var_assign('b', 10)
    cg.if_(('a', '==', 'b'))
    cg.call('Print', ['a == b'])
    cg.closeif()
    cg.else_if()
    cg.call('Print', ['a != b'])
    cg.closeif()
    cg.endif()
    cg.call('print', ['DONE'])
    print(cg.dump())


if __name__ == '__main__':
    main()
