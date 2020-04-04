import ply.lex as lex
import re

from .exceptions import IllegalCharacterError, UnterminatedStringError, UnterminatedCommentError


class UCLexer:
    """ A lexer for the uC language. After building it, set the
        input text with input(), and call token() to get new
        tokens.
    """
    def __init__(self, error_func):
        """ Create a new Lexer.
            An error function. Will be called with an error
            message, line and column as arguments, in case of
            an error during lexing.
        """
        self.error_func = error_func
        self.filename = ''

        # Keeps track of the last token returned from self.token()
        self.last_token = None

    def build(self, **kwargs):
        """ Builds the lexer from the specification. Must be
            called after the lexer object is created.

            This method exists separately, because the PLY
            manual warns against calling lex.lex inside __init__
        """
        self.lexer = lex.lex(object=self, **kwargs)

    def reset_lineno(self):
        """ Resets the internal line number counter of the lexer.
        """
        self.lexer.lineno = 1

    def input(self, text):
        self.lexer.input(text)

    def token(self):
        self.last_token = self.lexer.token()
        return self.last_token

    def find_tok_column(self, token):
        """ Find the column of the token in its line.
        """
        last_cr = self.lexer.lexdata.rfind('\n', 0, token.lexpos)
        return token.lexpos - last_cr

    # Internal auxiliary methods
    def _error(self, msg, token):
        location = self._make_tok_location(token)
        self.error_func(msg, location[0], location[1])
        self.lexer.skip(1)

    def _make_tok_location(self, token):
        return (token.lineno, self.find_tok_column(token))

    # Reserved keywords
    keywords = (
        'ASSERT', 'BREAK', 'CHAR', 'ELSE', 'FLOAT', 'FOR', 'IF',
        'INT', 'PRINT', 'READ', 'RETURN', 'VOID', 'WHILE',
    )

    keyword_map = {}
    for keyword in keywords:
        keyword_map[keyword.lower()] = keyword

    #
    # All the tokens recognized by the lexer
    #
    tokens = keywords + (
        'CCOMMENT', 'UCCCOMMENT', 'ID',
        'NUMBER', 'PLUS', 'PLUS_PLUS', 'MINUS',
        'MINUS_MINUS', 'TIMES', 'DIVIDE',
        'QUESTION', 'SEMI', 'COMMA',
        'UPPERSAND', 'AND', 'OR',
        'NOT', 'DIFFERENT', 'EQUAL',
        'SMALLER', 'SMALLER_EQUAL', 'BIGGER',
        'BIGGER_EQUAL', 'ASSIGN', 'ASSIGN_TIMES',
        'ASSIGN_DIVIDE', 'ASSIGN_REMAINDER', 'ASSIGN_PLUS',
        'ASSIGN_MINUS', 'INT_CONST', 'FLOAT_CONST',
        'STRING_CONST', 'LPAREN', 'RPAREN',
        'LBRACKET', 'RBRACKET', 'LBRACES', 'RBRACES'
    )

    #
    # Rules
    #
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
    t_EQUAL = r'=='
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
    t_RBRACKET = r'\]'
    t_LBRACES = r'{'
    t_RBRACES = r'}'
    t_ignore = ' \t'

    # Newlines
    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_ID(self, t):
        r'[a-zA-Z_][0-9a-zA-Z_]*'
        t.type = self.keyword_map.get(t.value, "ID")
        return t

    def t_CCOMMENT(self, t):
        r'/\*(.|\n)*?\*/'
        pass

    def t_UNTERMINATED_CCOMMENT(self, t):
        r'/\*(.|\n)*'
        msg = '{}'.format(UnterminatedCommentError("{}: Unterminated comment".format(t.lineno)))
        self._error(msg, t)
        pass

    def t_UCCOMMENT(self, t):
        r'//.*'
        pass

    def t_FLOAT_CONST(self, t):
        r'([0-9]*?\.[0-9]+)|([0-9]+\.)'
        t.value = float(t.value)
        return t

    def t_INT_CONST(self, t):
        r'0|[1-9][0-9]*'
        t.value = int(t.value)
        return t

    def t_STRING_CONST(self, t):
        r'".*?"'
        t.value = str(t.value)
        return t

    def t_UNTERMINATED_STRING(self, t):
        r'".*?'
        msg = '{}'.format(UnterminatedStringError("{}: Unterminated string".format(t.lineno)))
        self._error(msg, t)
        pass

    def t_error(self, t):
        msg = '{}'.format(IllegalCharacterError("Illegal character {}".format(t.value[0])))
        self._error(msg, t)

    # Scanner (used only for test)
    def scan(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)
