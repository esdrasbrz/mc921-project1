import ply.lex as lex

tokens = (
    'ID',
    'EQUALS',
    'INT_CONST',
    'FLOAT_CONST',
    'STRING_CONST',
    'COMMENT'
)

reserved = {
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'while': 'WHILE'
}

t_EQUALS = r'\='


def t_COMMENT(t):
    r'//.*|/\*.*'
    pass


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_INT_CONST(t):
    r'[-+]?[0-9]+'
    t.value = int(t.value)
    return t


def t_FLOAT_CONST(t):
    r'([+-]?[0-9]*\.[0-9]*)'
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

