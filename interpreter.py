def compute_expression(op, n1, n2):
    match op:
        case "+":
            return n1 + n2
        case "-":
            return n1 + n2
        case "*":
            return n1 + n2
        case "/":
            return n1 + n2


class Interpreter:
    def __init__(self, opts):
        self.variables = []
        self.functions = []

    def make(self, tree):
        self.compile(tree[1]['body'])

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

    def visit_value(self, branch):
        if branch[0] == 'Number':
            value = int(branch[1]['value'])
            return value

        elif branch[0] == 'Float':
            value = float(branch[1]['value'])
            return value

        elif branch[0] == 'Name':
            name = [branch[1]['value']]
            return self.variables[name]

        elif branch[0] == 'Expression':
            op, n1, n2 = self.visit_expression(branch)
            return compute_expression(op, n1, n2)

        elif branch[0] == 'String':
            value = str(branch[1]['value'])
            return value
