from asm_writer import RegOps, Int, Value, Variable, Def_Types, Variables, Registers, Expression, Register
import errors as xsErrors

START_FUNC = 'CMAIN'


class X64Registers:
    op1 = Register('rax')
    op2 = Register('rbx')
    all_ = [op1, op2]


class Codegen:
    data = ["section .data"]
    code = ["section .text", f"global {START_FUNC}"]
    segments = {
        f"{START_FUNC}": []
    }
    pkgs = []

    def __init__(self, opts):
        self.head = []
        self.opts = opts
        self.configure()
        self.cur = None
        self.prev = None
        self.heap_name = None
        self.set_cur(f'{START_FUNC}')

    def configure(self):
        for option in self.opts:
            if option == '64bit':
                self.include('io64.inc')
                global Registers
                Registers = X64Registers()
            elif option == '32bit':
                self.include('io.inc')

    def variables_dump(self):
        for var in Variables.variables_name.items():
            val = Variables.variables[var[1]]
            typ = val.type
            self.data.append(f'{var[1]} {Def_Types.find[typ]} {val.reprsentation()}')

    def set_cur(self, name):
        self.cur: list = self.segments[name]
        self.heap_name = name

    def gen_label_name(self):
        return f'SEG{len(self.segments)}'

    def bin_op(self, op, node1: Value, node2: Value, single_op=False, disable_info=False):
        # Move <node1> and <node2> to operation registers
        if not single_op:
            self.cur.append(RegOps.mov(Registers.op1, node1.reprsentation()))
            self.cur.append(RegOps.mov(Registers.op2, node2.reprsentation()))
        # Operation on <node1> and <node2>
        self.cur.append(RegOps.binaryOp(op, Registers.op1, Registers.op2))
        if node1.dst_ava:
            self.cur.append(RegOps.mov(node1.reprsentation(True), Registers.op1))
        else:
            if not disable_info:
                xsErrors.stdwarning('Operation has no effect')

    def new_segment(self, name, cur=True):
        self.segments[name] = []
        if cur:
            self.set_cur(name)

    def return_(self, value):
        self.cur.append(f'mov eax, {value.reprsentation()}')

    def retrieve_return_value(self, value: Value):
        self.cur.append(f'mov {value.reprsentation(True)}, eax')

    def make_end(self):
        self.cur.append(RegOps.jump('end'))
        self.new_segment('end')
        self.cur.append(RegOps.popall())
        self.bin_op('xor', Registers.op1, Registers.op1, True, True)

    def translate_expr_2_cmp(self, node1: Value, node2: Value):
        self.cur.append(RegOps.mov(Registers.op1, node1.reprsentation()))
        self.cur.append(RegOps.mov(Registers.op2, node2.reprsentation()))
        self.cur.append(f'cmp {Registers.op1}, {Registers.op2}')

    def if_start(self, op):
        name = self.gen_label_name()
        self.cur.append(RegOps.jump(name, op))
        self.new_segment(name)

    def out_if(self):
        self.set_cur(self.heap_name)

    def include(self, module):
        self.head.append(f"%include '{module}'")

    def dump(self):
        self.variables_dump()
        self.make_end()
        code = self.code + [""]
        start = self.segments.pop(f'{START_FUNC}')
        start[0] = "   " + start[0]
        start.append('ret')
        start = [f'{START_FUNC}:'] + ["\n   ".join(start)]
        for segment in self.segments.keys():
            value = self.segments[segment]
            value[0] = "   " + value[0]
            value.append('ret')
            value = "\n   ".join(value)
            value = [f'{segment}:'] + [value]
            value.append('')
            code = code + value
        full = self.head + self.data + code + start
        full = "\n".join(full)
        return full
