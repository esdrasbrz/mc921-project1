import ply.lex as lex

from lex.exceptions import IllegalCharacterError

reserved = {
    'if' : 'IF',
    'else' : 'ELSE',
    'while' : 'WHILE',
    'for' : 'FOR',
    'void': 'VOID',
    'char': 'CHAR',
    'int': 'INT',
    'float': 'FLOAT',
    'break': 'BREAK',
    'return': 'RETURN',
    'assert': 'ASSERT',
    'print': 'PRINT',
    'read': 'READ'
}

tokens = [
    'CCOMMENT',
    'UCCCOMMENT',
    'ID',
    'NUMBER',
    'PLUS',
    'PLUS_PLUS',
    'MINUS',
    'MINUS_MINUS',
    'TIMES',
    'DIVIDE',
    'QUESTION',
    'SEMI',
    'COMMA',
    'UPPERSAND',
    'AND',
    'OR',
    'NOT',
    'DIFFERENT',
    'EQUAL',
    'SMALLER',
    'SMALLER_EQUAL',
    'BIGGER',
    'BIGGER_EQUAL',
    'ASSIGN',
    'ASSIGN_TIMES',
    'ASSIGN_DIVIDE',
    'ASSIGN_REMAINDER',
    'ASSIGN_PLUS',
    'ASSIGN_MINUS',
    'INT_CONST',
    'FLOAT_CONST',
    'STRING_CONST',
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'LBRACES',
    'RBRACES'
] + list(reserved.values())

# Operators
t_PLUS = r'\+'
t_PLUS_PLUS = r'\+\+'
t_MINUS = r'-'
t_MINUS_MINUS = r'--'
t_TIMES = r'\*'
t_DIVIDE = r'/'

# Helper symbols
t_SEMI = r';'
t_COMMA = r','
t_QUESTION = r'\?'
t_UPPERSAND = '&'

# Logic symbols
t_OR = r'\|\|'
t_AND = r'&&'
t_NOT = r'!'

# Comparison symbols
t_DIFFERENT = r'!='
t_EQUAL= r'=='
t_SMALLER = r'<'
t_SMALLER_EQUAL = r'<='
t_BIGGER = r'>'
t_BIGGER_EQUAL = r'<='

# Assign symbols
t_ASSIGN = r'\='
t_ASSIGN_TIMES = r'\*='
t_ASSIGN_DIVIDE = r'/='
t_ASSIGN_REMAINDER = r'%='
t_ASSIGN_PLUS = r'\+='
t_ASSIGN_MINUS = r'-='

# Left Right symbols
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET  = r'\]'
t_LBRACES = r'{'
t_RBRACES = r'}'



def t_CCOMMENT(t):
    r'/\*(.|\n)*?\*/'
    pass


def t_UCCOMMENT(t):
    r'//.*'
    pass


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_FLOAT_CONST(t):
    r'([0-9]*?\.[0-9]+)|([0-9]+\.)'
    t.value = float(t.value)
    return t


def t_INT_CONST(t):
    r'0|[1-9][0-9]*'
    t.value = int(t.value)
    return t


def t_STRING_CONST(t):
    r'".*?"'
    t.value = str(t.value)
    return t


t_ignore = ' \t'


def t_error(t):
    raise IllegalCharacterError("Illegal character {}".format(t.value[0]))


lexer = lex.lex()

