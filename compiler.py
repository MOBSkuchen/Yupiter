import os.path
from sly import Lexer, Parser
from codegen import Codegen
from asm_writer import RegOps, Int, Value, Variable, Def_Types, Variables, Registers, Expression, Float, String
import errors as xsErrors
from sly.yacc import YaccProduction

__version__ = '1.0'


class utils:
    @staticmethod
    def data(Type, value, pos):
        return Type, {'value': value}, pos

    @staticmethod
    def list(value, Type, pos):
        return 'List', {'value': value, 'type': Type}, pos

    @staticmethod
    def dot(e1, e2, e3, pos):
        return 'Dot', {'obj': e1, 'function': e2, 'args': e3}, pos

    @staticmethod
    def import_s(module, pos):
        return 'Import', {'module': module}, pos

    @staticmethod
    def expression(op, lhs, rhs, pos):
        return 'Expression', {'op': op, 'lhs': lhs, 'rhs': rhs}, pos

    @staticmethod
    def var_assign(name, value, pos):
        return 'VarAssign', {'value': value, 'name': name}, pos

    @staticmethod
    def set(name, value, pos, size=None):
        return 'VarSet', {'type': value, 'name': name, 'size': size}, pos

    @staticmethod
    def if_stmt(body, orelse, test, pos):
        return 'If', {'body': body, 'test': test, 'orelse': orelse}, pos

    @staticmethod
    def while_block(body, test, pos):
        return 'While', {'test': test, 'body': body}, pos

    @staticmethod
    def until_block(body, test, pos):
        return 'Until', {'test': test, 'body': body}, pos

    @staticmethod
    def func_call(name, params, pos):
        return 'FuncCall', {'params': params, 'name': name}, pos

    @staticmethod
    def function(name, def_params, body, pos):
        return 'Def', {'name': name, 'body': body, 'def_params': def_params if def_params else []}, pos


def group(*choices): return '(' + '|'.join(choices) + ')'


def any(*choices): return group(*choices) + '*'


def maybe(*choices): return group(*choices) + '?'


Hexnumber = r'0[xX](?:_?[0-9a-fA-F])+'
Binnumber = r'0[bB](?:_?[01])+'
Octnumber = r'0[oO](?:_?[0-7])+'
Decnumber = r'(?:0(?:_?0)*|[1-9](?:_?[0-9])*)'
Exponent = r'[eE][-+]?[0-9](?:_?[0-9])*'
Pointfloat = group(r'[0-9](?:_?[0-9])*\.(?:[0-9](?:_?[0-9])*)?',
                   r'\.[0-9](?:_?[0-9])*') + maybe(Exponent)
Expfloat = r'[0-9](?:_?[0-9])*' + Exponent


# noinspection PyUnresolvedReferences,PyUnboundLocalVariable,PyPep8Naming,PyMethodMayBeStatic,PyRedeclaration
class PLexer(Lexer):
    tokens = {
        NAME,
        NUMBER,
        STRING,
        FLOAT,
        PLUS,
        MINUS,
        DIVIDE,
        LPAREN,
        RPAREN,
        SEMI_COLON,
        LT,
        LE,
        GT,
        GE,
        EQ,
        EQEQ,
        NE,
        IF,
        ELSE,
        DEF,
        RETURN,
        TIMES,
        COLON,
        MOD,
        WHILE,
        UNTIL,
        BREAK,
        CONTINUE,
        AND,
        OR,
        COMMA,
        SET,
        IMPORT,
    }

    literals = {',', ';'}

    FLOAT = group(Pointfloat, Expfloat)

    NUMBER = group(
        Hexnumber,
        Binnumber,
        Octnumber,
        Decnumber
    )

    ignore = ' \t\r'

    @_(r'\n')
    def newline(self, t):
        self.lineno += 1

    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    NAME['if'] = IF
    NAME['else'] = ELSE
    NAME['def'] = DEF
    NAME['return'] = RETURN
    NAME['while'] = WHILE
    NAME['until'] = UNTIL
    NAME['break'] = BREAK
    NAME['continue'] = CONTINUE
    NAME['and'] = AND
    NAME['or'] = OR
    NAME['set'] = SET
    NAME['import'] = IMPORT
    STRING = r'(\".*?\")|(\'.*?\')'
    GE = r'>='
    GT = r'>'
    LE = r'<='
    LT = r'<'
    NE = r'!='
    EQEQ = r'=='
    EQ = r'='
    LPAREN = r'\('
    RPAREN = r'\)'
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    MOD = r'%'
    COLON = r':'
    SEMI_COLON = r';'
    COMMA = r','

    @_(r'#.*')
    def COMMENT(self, t):
        pass

    def error(self, t):
        xsErrors.stderr(3, (t.index, t.index), t.lineno, f'Illegal character "{t.value[0]}"')


class MutedLogger(object):
    def __init__(self, f):
        self.f = f

    def debug(self, msg, *args, **kwargs):
        self.f.write((msg % args) + '\n')

    info = debug

    def warning(self, msg, *args, **kwargs):
        xsErrors.stdwarning(msg % args)

    @staticmethod
    def error(self, token, *args):
        if token:
            lineno = getattr(token, 'lineno', 0)
            index = getattr(token, 'index', -1)
            end = getattr(token, 'end', -1) - 1
            if lineno:
                xsErrors.stderr(5, (index, end), lineno, f'Invalid token ({token.type})')
            else:
                xsErrors.stderr(5, (index, end), -1, f'Invalid token ({token.type})')
        else:
            xsErrors.stderr(5, (getattr(token, 'index', -1), getattr(token, 'lineno', 0)), -1, f'Empty file')

    critical = debug


Parser2 = Parser
Parser2.log = MutedLogger(None)
Parser2.error = Parser2.log.error


# noinspection PyUnresolvedReferences,PyUnboundLocalVariable,PyPep8Naming,PyMethodMayBeStatic,PyRedeclaration
class PParser(Parser2):
    tokens = PLexer.tokens

    precedence = (
        ('nonassoc', NE, LT, LE, GT, GE, EQEQ),
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE)
    )

    def __init__(self):
        self.ast = ('Module', {'body': []})

    @_("statements")
    def body(self, p):
        self.ast[1]['body'] = p.statements

    @_('statement')
    def statements(self, p):
        return [p.statement]

    @_('statements statement')
    def statements(self, p):
        p.statements.append(p.statement)
        return p.statements

    @_('RETURN expr')
    def statement(self, p):
        return 'Return', {'value': p.expr}

    @_('BREAK')
    def statement(self, p):
        return 'BREAK', {}

    @_('CONTINUE')
    def statement(self, p):
        return 'CONTINUE', {}

    @_('DEF NAME LPAREN def_params RPAREN  statements SEMI_COLON')
    def statement(self, p):
        return utils.function(p.NAME, p.def_params, p.statements, (getattr(p, 'index', -1), getattr(p, 'lineno', 0)))

    @_('IF expr  statements SEMI_COLON')
    def statement(self, p):
        return utils.if_stmt(p.statements, pos=(getattr(p, 'index', -1), getattr(p, 'lineno', 0)), orelse=[], test=p.expr)

    @_('IF expr  statements SEMI_COLON ELSE  statements SEMI_COLON')
    def statement(self, p):
        return utils.if_stmt(p.statements0, p.statements1, p.expr, (getattr(p, 'index', -1), getattr(p, 'lineno', 0)))

    @_('WHILE expr statements SEMI_COLON')
    def statement(self, p):
        return utils.while_block(p.statements, p.expr, (getattr(p, 'index', -1), getattr(p, 'lineno', 0)))

    @_('UNTIL expr statements SEMI_COLON')
    def statement(self, p):
        return utils.until_block(p.statements, p.expr, (getattr(p, 'index', -1), getattr(p, 'lineno', 0)))

    @_('IMPORT NAME')
    def statement(self, p):
        return utils.import_s(p.NAME, (getattr(p, 'index', -1), getattr(p, 'lineno', 0)))

    @_('NAME EQ expr')
    def statement(self, p):
        return utils.var_assign(p.NAME, p.expr, (getattr(p, 'index', -1), getattr(p, 'lineno', 0)))

    @_('SET NAME COLON NAME EQ NUMBER')
    def statement(self, p):
        return utils.set(p.NAME0, p.NAME1, (getattr(p, 'index', -1), getattr(p, 'lineno', 0)), size=p.NUMBER)

    @_('SET NAME COLON NAME')
    def statement(self, p):
        return utils.set(p.NAME0, p.NAME1, (getattr(p, 'index', -1), getattr(p, 'lineno', 0)))

    @_('NAME LPAREN params RPAREN')
    def statement(self, p):
        return utils.func_call(p.NAME, p.params, (getattr(p, 'index', -1), getattr(p, 'lineno', 0)))

    @_('def_params COMMA def_param')
    def def_params(self, p):
        p.def_params.append(p.def_param)
        return p.def_params

    @_('def_param')
    def def_params(self, p):
        return [p.def_param]

    @_('NAME COLON NAME')
    def def_param(self, p):
        return {'name': p.NAME0, 'type': p.NAME1}

    @_('')
    def def_param(self, p):
        return

    @_('params COMMA param')
    def params(self, p):
        p.params.append(p.param)
        return p.params

    @_('param')
    def params(self, p):
        return [p.param]

    @_('expr')
    def param(self, p):
        return p.expr

    @_('')
    def param(self, p):
        return

    @_('NAME LPAREN params RPAREN')
    def expr(self, p):
        return utils.func_call(p.NAME, p.params, (getattr(p, 'index', -1), getattr(p, 'lineno', 0)))

    @_('expr PLUS expr',
       'expr MINUS expr',
       'expr TIMES expr',
       'expr DIVIDE expr',
       'expr MOD expr',
       'expr GT expr',
       'expr GE expr',
       'expr LT expr',
       'expr LE expr',
       'expr NE expr',
       'expr EQEQ expr',
       'expr AND expr',
       'expr OR expr')
    def expr(self, p):
        return utils.expression(p[1], p.expr0, p.expr1, (getattr(p, 'index', -1), getattr(p, 'lineno', 0)))

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr

    @_('NAME')
    def expr(self, p):
        return utils.data('Name', p.NAME, (getattr(p, 'index', -1), getattr(p, 'lineno', 0)))

    @_('NUMBER')
    def expr(self, p):
        return utils.data('Number', int(p.NUMBER), (getattr(p, 'index', -1), getattr(p, 'lineno', 0)))

    @_('MINUS NUMBER')
    def expr(self, p):
        return utils.data('Number', int(p.NUMBER) * -1, (getattr(p, 'index', -1), getattr(p, 'lineno', 0)))

    @_('FLOAT')
    def expr(self, p):
        return utils.data('Float', float(p.FLOAT), (getattr(p, 'index', -1), getattr(p, 'lineno', 0)))

    @_('MINUS FLOAT')
    def expr(self, p):
        return utils.data('Float', float(p.FLOAT) * -1, (getattr(p, 'index', -1), getattr(p, 'lineno', 0)))

    @_('STRING')
    def expr(self, p):
        return utils.data('String', p.STRING, (getattr(p, 'index', -1), getattr(p, 'lineno', 0)))


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

        self.cg.function(name, params)
        self.compile(body)

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
