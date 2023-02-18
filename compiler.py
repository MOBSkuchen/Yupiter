import os.path
from codegen import Codegen
from asm_writer import RegOps, Int, Value, Variable, Def_Types, Variables, Registers, Expression, Float, String
import errors as xsErrors


class Compiler:
    def __init__(self, opts):
        self.cg = Codegen(opts)

    def make(self, tree):
        self.compile(tree[1]['body'])
        return self.cg.dump()

    def compile(self, ast):
        for branch in ast:
            if branch[0] == 'VarAssign':
                self.visit_assign(branch)
            elif branch[0] == 'Def':
                self.visit_def(branch)
            elif branch[0] == 'Return':
                self.visit_return(branch)
            elif branch[0] == 'Import':
                self.visit_import(branch)
            elif branch[0] == 'VarSet':
                self.visit_set(branch)
            elif branch[0] == 'FuncCall':
                self.visit_func_call(branch)

    def visit_set(self, branch):
        name = branch[1]['name']
        type_ = branch[1]['type']
        size = branch[1]['size']
        pos = branch[2][0], branch[2][1]

        if size and size.isnumeric() and int(size) > 10000:
            xsErrors.stderr(7, pos[0], pos[1], "Reservation size is > 10,000", True)
        elif size and not size.isnumeric():
            xsErrors.stdwarning("Reservation size is not numeric")

        self.cg.set(name, size, type_)

    def visit_import(self, branch):
        name = branch[1]['module']
        name = os.path.abspath(os.path.join(os.curdir, 'include', name + ".inc"))
        pos = branch[2]
        if not os.path.exists(name):
            xsErrors.stderr(6, (pos[0], pos[0]), pos[1], f"Module not found '{name}'", True)
            return
        self.cg.include(name)

    def visit_def(self, branch):
        name = branch[1]['name']
        body = branch[1]['body']
        params = branch[1]['def_params']

        x = self.cg.heap_name
        self.cg.function(name, params)
        self.compile(body)
        self.cg.set_cur(x)

    def visit_func_call(self, branch):
        name = branch[1]["name"]
        params = branch[1]["params"]
        pos = branch[2]

        x = self.cg.run_function(name)
        if x == 10:
            xsErrors.stderr(1, (pos[0], pos[0]), pos[1], f"Function could not be found", True)

    def visit_value(self, branch):
        if branch[0] == 'Number':
            value = Int(int(branch[1]['value']))
            return value

        elif branch[0] == 'Float':
            value = Float(float(branch[1]['value']))
            return value

        elif branch[0] == 'Name':
            name = Variables.variables_name[branch[1]['value']]
            return Variable(name, Variables.variables[name], False)

        elif branch[0] == 'Expression':
            op, n1, n2 = self.visit_expression(branch)
            return Expression(op, n1, n2, self.cg)

        elif branch[0] == 'String':
            value = String(str(branch[1]['value']))
            return value

    def visit_assign(self, branch):
        name = branch[1]['name']
        if name.startswith("__") and name.endswith('__'):
            xsErrors.stderr(1, (branch[2][0], branch[2][0]), branch[2][1], "Names starting and ending with a DUNDER are reserved", 1)
        value = branch[1]['value']
        value: Value = self.visit_value(value)
        if type(value) == Expression:
            v = Variable(Variables.new(), Int(0)) if not name in Variables.variables_name else Variables.get_as_obj(Variables.variables_name[name])
            # Optimization
            if type(value.node1) == Variable and v.name != value.node1.name:
                self.cg.shift(value.node1, v)
            else:
                if type(value.node1) != Variable:
                    self.cg.shift(value.node1, v)
        else:
            if not Variables.exists_reg(name):
                Variable(name, value)
            else:
                self.cg.cur.append(RegOps.mov(Variables.get_as_obj(Variables.variables_name[name]).representation(True), value.representation()))

    def visit_return(self, branch):
        value = branch[1]['value']
        value = self.visit_value(value)
        self.cg.return_(value)

    def visit_expression(self, branch):
        op = branch[1]['op']
        lhs: Value = self.visit_value(branch[1]['lhs'])
        rhs: Value = self.visit_value(branch[1]['rhs'])
        return op, lhs, rhs
