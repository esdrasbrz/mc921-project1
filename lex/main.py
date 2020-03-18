import ply.lex as lex

tokens = (
    'CCOMMENT',
    'UCCCOMMENT',
    'ID',
    'EQUALS',
    'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'INT_CONST',
    'FLOAT_CONST',
    'STRING_CONST',
)

t_EQUALS = r'\='
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'


def t_CCOMMENT(t):
    r'/\*(.|\n)*?\*/'
    pass


def t_UCCOMMENT(t):
    r'//.*'
    pass


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_INT_CONST(t):
    r'0|[1-9][0-9]*'
    t.value = int(t.value)
    return t


def t_FLOAT_CONST(t):
    r'([0-9]*\.[0-9]+)|([0-9]+\.)'
    t.value = float(t.value)
    return t


def t_STRING_CONST(t):
    r'["][\w\s]+["]'
    t.value = str(t.value)
    return t


t_ignore = ' \t'


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()

