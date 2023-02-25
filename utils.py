import struct


class Variables:
    variables_name = {}
    variables = {}
    emg = None
    c = 0
    c2 = -1
    c3 = -1

    @staticmethod
    def exists_reg(item):
        return item in Variables.variables_name

    @staticmethod
    def get_as_obj(item):
        return Variable(item, Variables.variables[item], False)

    @staticmethod
    def new():
        Variables.c3 += 1
        return f'__sys{Variables.c3}__'

    @staticmethod
    def define_var(name, value):
        Variables.variables[name] = value

    @staticmethod
    def assign(name, uninit=False, func=False):
        if name in Variables.variables_name.keys():
            Variables.emg = Variables.variables_name[name]
        else:
            Variables.emg = None
        if not uninit:
            Variables.variables_name[name] = f'{"F" if func else "v"}{Variables.c}'
        else:
            Variables.variables_name[name] = f'u{Variables.c}'
        Variables.c += 1
        return Variables.variables_name[name]

    @staticmethod
    def location():
        Variables.c2 += 1
        return f'l_{Variables.c2}'


class IV_Types:
    string = 'str'
    int_ = 'int'
    float_ = 'float'
    bool_ = 'bool'
    null = 'null'
    find = {
        'str': string,
        'int': int_,
        'float': float_,
        'bool': bool_,
        'null': null,
    }


class Def_Types:
    string = 'db'
    int_ = 'db'
    float_ = 'db'
    bool_ = 'db'
    null = 'db'
    find = {
        'str': string,
        'int': int_,
        'float': float_,
        'bool': bool_,
        'null': null,
    }


class Value:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value
        self.dst_ava = False

    def __repr__(self):
        return f'{self.type} : {self.value}'

    def representation(self, dst=False):
        return f'{self.value}'


class Null(Value):
    def __init__(self):
        super().__init__(IV_Types.null, 'NULL')


class Register(Value):
    def __init__(self, value):
        super(Register, self).__init__('reg', value)

    def __str__(self):
        return self.representation(None)


def float_to_hex(f):
    return hex(struct.unpack('<I', struct.pack('<f', f))[0])


class Registers:
    op1 = Register('eax')
    op2 = Register('ebx')
    all_ = [op1, op2]


class Variable(Value):
    def __init__(self, name, value, eng=True):
        self.iv_value = value
        self.name = name
        self.dst_ava = True
        self.uninit = value is None
        if self.uninit:
            self.iv_value = Null()
        if eng:
            self.cover = Variables.assign(self.name, self.uninit)
            Variables.define_var(self.cover, self.iv_value if not self.uninit else Null())
        else:
            self.cover = self.name

        super(Variable, self).__init__(self.iv_value.type, self.iv_value.value)

    def __repr__(self):
        return f'{self.name} = {self.type} : {self.value}'

    def representation(self, dst=False):
        return f'[{self.cover}]' if dst else f'{self.cover}'


class String(Value):
    def __init__(self, value):
        super(String, self).__init__(IV_Types.string, value)


class Int(Value):
    def __init__(self, value):
        super(Int, self).__init__(IV_Types.int_, value)


class Float(Value):
    def __init__(self, value):
        super(Float, self).__init__(IV_Types.float_, value)

    def representation(self, dst=False):
        return f'{float_to_hex(self.value)}'


class Expression(Value):
    def __init__(self, op, node1, node2, base):
        self.op = op
        self.node1: Value = node1
        self.node2: Value = node2

        self.type = self.node1.type
        self.value = self.node1.value

        self.dst_ava = self.node1.dst_ava

        base.bin_op(self.op, self.node1, self.node2)

    def representation(self, dst=False):
        return self.node1.representation(dst)


class RegOps:
    @staticmethod
    def compare(op1, op2):
        return f'cmp {op1}, {op2}'

    @staticmethod
    def mov(op1, op2):
        return f'mov {op1}, {op2}'

    @staticmethod
    def jump(label, cond=None):
        match cond:
            case None:
                return f'jmp {label}'
            case "==":
                return f'je {label}'

    @staticmethod
    def binaryOp(op, node1, node2):
        match op:
            case "+":
                op = 'add'
            case "-":
                op = 'sub'
            case _:  # Use default OP
                pass
        return f'{op} {node1}, {node2}'

    @staticmethod
    def pop(x):
        return f'pop {x}'

    @staticmethod
    def push(x):
        return f'push {x}'

    @staticmethod
    def popall(big=True):
        return f';popad' if big else ';popa'
