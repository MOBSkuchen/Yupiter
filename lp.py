from sly import Lexer, Parser
from codegen import Codegen

__version__ = '1.0'


def group(*choices): return '(' + '|'.join(choices) + ')'


def any_(*choices): return group(*choices) + '*'


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
        DOT,
        EXM,
        QM
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
    EXM = r'!'
    LPAREN = r'\('
    RPAREN = r'\)'
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    MOD = r'%'
    COLON = r':'
    DOT = r'\.'
    SEMI_COLON = r';'
    QM = r'\?'
    COMMA = r','

    @_(r'#.*')
    def COMMENT(self, t):
        pass

    def error(self, t):
        print(f'Illegal character {t.value[0]}, in line {self.lineno}, index {self.index}')
        exit()


class MutedLogger(object):
    def debug(self, *args):
        pass

    def warning(self, *args):
        pass

    def error(self, *args):
        pass


class SyntaxErr(Exception):
    def __init__(self, *args, **kwargs):
        pass


class ParserErr(Exception):
    def __init__(self, *args, **kwargs):
        pass


def error(self, token):
    if token:
        lineno = getattr(token, 'lineno', 0)
        if lineno:
            raise SyntaxErr(lineno, token.type)
        else:
            raise SyntaxErr(-1, token.type)
    else:
        raise ParserErr()


Parser2 = Parser
Parser2.error = error
Parser2.log = MutedLogger()


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
        self.cg = Codegen([], [])
        self.eax_move = False

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
        self.cg.return_(p.expr)

    @_('BREAK')
    def statement(self, p):
        return 'BREAK', {}

    @_('CONTINUE')
    def statement(self, p):
        return 'CONTINUE', {}

    @_('def_head  statements SEMI_COLON')
    def statement(self, p):
        # self.cg.function(p.NAME, p.def_params)
        self.cg.close_function()

    @_('DEF NAME LPAREN def_params RPAREN')
    def def_head(self, p):
        self.cg.function(p.NAME, p.def_params)

    @_('if_start  statements SEMI_COLON')
    def statement(self, p):
        # self.cg.if_(p.expr)
        self.cg.if_close()

    @_('IF expr')
    def if_start(self, p):
        self.cg.if_(p.expr)

    #@_('WHILE expr statements SEMI_COLON')
    #def statement(self, p):
    #    return utils.while_block(p.statements, p.expr)

    #@_('UNTIL expr statements SEMI_COLON')
    #def statement(self, p):
    #    return utils.until_block(p.statements, p.expr)

    @_('IMPORT NAME')
    def statement(self, p):
        self.cg.import_(p.NAME)

    @_('IMPORT QM EXM NAME')
    def statement(self, p):
        self.cg.include_lib(p.NAME)

    @_('IMPORT QM NAME')
    def statement(self, p):
        self.cg.include(p.NAME)

    @_('NAME EQ expr')
    def statement(self, p):
        value = p.expr
        if self.eax_move:
            value = 'NULL'
        self.cg.var_assign(p.NAME, value)
        if self.eax_move:
            self.cg.get_after_return(p.NAME)
            self.eax_move = False

    @_('NAME LPAREN params RPAREN')
    def statement(self, p):
        self.cg.call(p.NAME, p.params)

    @_('def_params COMMA def_param')
    def def_params(self, p):
        p.def_params.append(p.def_param)
        return p.def_params

    @_('def_param')
    def def_params(self, p):
        return [p.def_param]

    @_('NAME')
    def def_param(self, p):
        return p.NAME

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
        self.cg.call(p.NAME, p.params)
        self.eax_move = True

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
        return p.expr0, p[1], p.expr1

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr

    @_('NAME')
    def expr(self, p):
        return p.NAME, True

    @_('NUMBER')
    def expr(self, p):
        return int(p.NUMBER)

    @_('MINUS NUMBER')
    def expr(self, p):
        return int(p.NUMBER) * -1

    @_('FLOAT')
    def expr(self, p):
        return float(p.FLOAT)

    @_('MINUS FLOAT')
    def expr(self, p):
        return float(p.FLOAT) * -1

    @_('STRING')
    def expr(self, p):
        return p.STRING
