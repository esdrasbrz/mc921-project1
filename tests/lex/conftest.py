import pytest
from lex.main import lexer
from lex.uc_lexer import UCLexer


@pytest.fixture
def lex():

    def print_error(msg, x, y):
        print("Lexical error: %s at %d:%d" % (msg, x, y))

    lex = UCLexer(print_error)
    lex.build()
    return lex
