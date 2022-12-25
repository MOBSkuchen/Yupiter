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
    "var_assign": "{name} db {value}, 0"
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
    def var_assign(name, value):
        return func_table["var_assign"].format(name=name, value=value)

    @staticmethod
    def start_begin():
        return 'start:'

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


class Codegen:
    data = [".data"]
    code = [Codes.start_begin()]
    head = []
    heap = []
    pkgs = []
    last_func = None
    in_func = False

    def __init__(self, imports, import_libs):
        self.head.append(".386")
        self.head.append(".model flat, stdcall")
        self.head.append("option casemap: none ; CASE SENSITIVE = ON")
        Variables.register()
        for import_ in imports:
            self.include(import_)
        for import_ in import_libs:
            self.include_lib(import_)

    def include(self, name):
        if name in self.pkgs:
            return
        self.pkgs.append(name)
        self.head.append(Codes.include(name))

    def include_lib(self, name):
        if name in self.pkgs:
            return
        self.pkgs.append(name)
        self.head.append(Codes.include_lib(name))

    def import_(self, name):
        if name in self.pkgs:
            return
        self.pkgs.append(name)
        self.head.append(Codes.import_(name))

    def if_(self, expr):
        expr = self.parse_expr(expr)
        self.heap.append(Codes.if_(expr))

    def elif_(self, expr):
        expr = self.parse_expr(expr)
        self.heap.append(Codes.elif_(expr))

    def else_(self):
        self.heap.append(Codes.else_())

    def if_close(self):
        self.heap.append(Codes.if_close())

    def parse_expr(self, expr):
        lhs, op, rhs = expr
        if type(lhs) != str:
            lhs = self.parse_expr(expr)
        else:
            lhs = Variables.variables[lhs]
        if type(lhs) != str:
            rhs = self.parse_expr(expr)
        else:
            rhs = Variables.variables[rhs]
        return f'{lhs} {op} {rhs}'

    def return_(self, expr):
        expr = self.parse_expr(expr)
        self.heap.append(Codes.move('eax', expr))

    def get_after_return(self, var):
        var = Variables.variables[var]
        self.heap.append(Codes.move(var, 'eax'))

    def comb(self, args):
        x = []
        for arg in args:
            print(arg)
            if type(arg) != tuple:
                var = False
                argx = arg
            else:
                argx, var = arg
                argx = Variables.variables[argx]
            x.append(argx if not var else f'addr {argx}')
        return ",".join(x)

    def call(self, name, args):
        name = Variables.variables[name] if name in Variables.variables else name
        args = self.comb(args)
        self.heap.append(Codes.invoke(name, args))

    def function(self, name, args):
        self.in_func = True
        name = Variables.assign(name, True)
        self.last_func = name
        p = Codes.define_function(name, len(args))
        x = []
        for i in args:
            x.append(Variables.assign(i))
        q = Codes.declare_function(name, x)
        self.head.append(p)
        self.heap.append(q)
        self.heap_dump()

    def close_function(self, name=None):
        self.heap_dump()
        if name is None:
            name = self.last_func
        else:
            name = Variables.variables[name]
        self.heap.append(Codes.end_func(name))
        self.in_func = False

    def var_assign(self, name, value):
        name = Variables.assign(name)
        self.data.append(Codes.var_assign(name, value))
        if Variables.emg:
            self.heap.append(Codes.var_clear(Variables.emg))

    def heap_dump(self):
        #if self.in_func:
        #    self.code = self.heap + self.code
        #else:
        self.code = self.code + self.heap
        self.heap = []

    def add_exit(self):
        self.heap.append(Codes.invoke("Exit", "0"))
        self.import_('stdlib')

    def dump(self):
        self.add_exit()
        self.heap_dump()
        self.code = [".code"] + self.code
        self.code.append(Codes.start_end())
        data = "\n".join(self.data)
        code = "\n".join(self.code)
        head = "\n".join(self.head)
        return f'{head}\n{data}\n{code}'
