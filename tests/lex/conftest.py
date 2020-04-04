import pytest

from parser.lex.uc_lexer import UCLexer
from parser.lex.exceptions import LexerError


@pytest.fixture
def lex():

    def print_error(msg, x, y):
        raise LexerError("\nLexer error: %s at %d:%d" % (msg, x, y))

    lex = UCLexer(print_error)
    lex.build()

    return lex
