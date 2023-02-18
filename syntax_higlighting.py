import json
import colorama as colora
from sly import Lexer
from sly.lex import Token


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
        INDENT,
        EMPTY,
        ERROR
    }

    literals = {',', ';'}

    FLOAT = group(Pointfloat, Expfloat)

    NUMBER = group(
        Hexnumber,
        Binnumber,
        Octnumber,
        Decnumber
    )

    #ignore = '\t\r'

    def __init__(self):
        self.toks = []

    @_(r'\n')
    def newline(self, t):
        self.lineno += 1
        self.toks.append(t)

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
    INDENT = r'   '
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
    EMPTY = r' '

    @_(r'#.*')
    def COMMENT(self, t):
        self.toks.append(t)

    def error(self, t):
        t.type = 'ERROR'
        self.toks.append(t)
        pass

    def tokenize(self, text, lineno=1, index=0):
        _ignored_tokens = _master_re = _ignore = _token_funcs = _literals = _remapping = None

        # --- Support for state changes
        def _set_state(cls):
            nonlocal _ignored_tokens, _master_re, _ignore, _token_funcs, _literals, _remapping
            _ignored_tokens = cls._ignored_tokens
            _master_re = cls._master_re
            _ignore = cls.ignore
            _token_funcs = cls._token_funcs
            _literals = cls.literals
            _remapping = cls._remapping

        self.__set_state = _set_state
        _set_state(type(self))

        # --- Support for backtracking
        _mark_stack = []
        def _mark():
            _mark_stack.append((type(self), index, lineno))
        self.mark = _mark

        def _accept():
            _mark_stack.pop()
        self.accept = _accept

        def _reject():
            nonlocal index, lineno
            cls, index, lineno = _mark_stack[-1]
            _set_state(cls)
        self.reject = _reject


        # --- Main tokenization function
        self.text = text
        try:
            while True:
                try:
                    if text[index] in _ignore:
                        index += 1
                        continue
                except IndexError:
                    return

                tok = Token()
                tok.lineno = lineno
                tok.index = index
                m = _master_re.match(text, index)
                if m:
                    tok.end = index = m.end()
                    tok.value = m.group()
                    tok.type = m.lastgroup

                    if tok.type in _remapping:
                        tok.type = _remapping[tok.type].get(tok.value, tok.type)

                    if tok.type in _token_funcs:
                        self.index = index
                        self.lineno = lineno
                        tok = _token_funcs[tok.type](self, tok)
                        index = self.index
                        lineno = self.lineno
                        if not tok:
                            continue

                    if tok.type in _ignored_tokens:
                        continue

                    self.toks.append(tok)

                else:
                    # No match, see if the character is in literals
                    if text[index] in _literals:
                        tok.value = text[index]
                        tok.end = index + 1
                        tok.type = tok.value
                        index += 1
                        self.toks.append(tok)
                    else:
                        # A lexing error
                        self.index = index
                        self.lineno = lineno
                        tok.type = 'ERROR'
                        tok.value = text[index:]
                        tok = self.error(tok)
                        if tok is not None:
                            tok.end = self.index
                            self.toks.append(tok)

                        index = self.index
                        lineno = self.lineno

        # Set the final state of the lexer before exiting (even if exception)
        finally:
            self.text = text
            self.index = index
            self.lineno = lineno


def translate_color(x):
    fg = colora.Fore
    if x.startswith('b:'):
        fg = colora.Back
        x = x[2:]
    match x:
        case "none":
            return ""
        case "red":
            return fg.RED
        case "dark_red":
            return fg.LIGHTRED_EX
        case "lmag":
            return fg.LIGHTMAGENTA_EX
        case "grey":
            return fg.LIGHTBLACK_EX
        case "yellow":
            return fg.YELLOW
        case "green":
            return fg.GREEN
        case "blue":
            return fg.BLUE
        case "dim":
            return colora.Style.BRIGHT
        case "orange":
            return fg.LIGHTMAGENTA_EX


def readfile(filename):
    with open(filename, 'r') as filereader:
        content = filereader.read()
    return content


def tokenize(content, dictionary):
    r = []
    s = []
    tokens_ = dict(dictionary["tokens"])
    colgroups = dict(dictionary["colgroups"])
    lexer = PLexer()
    lexer.tokenize(content)
    for token in lexer.toks:
        v = False
        if token.type == 'EMPTY':
            continue
        if token.type == 'INDENT':
            token.value = '   '
            v = True
            co = colgroups[tokens_[token.type]]
        elif token.type in tokens_.keys():
            co = colgroups[tokens_[token.type]]
        else:
            co = colgroups["0"]
        c = token.value
        full = f'{colora.Style.RESET_ALL}{translate_color(co)}{c}{colora.Style.RESET_ALL}'
        if v:
            full = f'{colora.Style.RESET_ALL}{translate_color(co)}{c}'
        if c == "\n":
            s.append(" ".join(r))
            r = []
        else:
            r.append(full)
    return "\n".join(s)


def light(c):
    v = json.loads(readfile('syntax.json'))
    x = tokenize(c, v)
    return x
