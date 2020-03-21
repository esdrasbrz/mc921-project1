import pytest
from lex.main import lexer


@pytest.fixture
def lex():
    return lexer
