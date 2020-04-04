import pytest

from tests.conftest import read_files
from .data import *


def test_lex_identifiers(lex, tests):
    """
    Integration test for the lex, tests identifiers
    :return:
    """

    lex.input(tests[0])
    output = ""
    while True:
        tok = lex.token()
        if not tok:
            break  # No more input
        output += "{}\n".format(tok)
    output = output.rstrip('\n')
    assert output == tests[1]

    pass


def test_lex_reserved(lex):
    """
    Integration test for the lex, tests reserved keywords
    :return:
    """
    lex.input(lex_reserved_test)

    while True:
        tok = lex.token()
        if not tok:
            break  # No more input
    pass


def test_lex_all(lex):
    """
    Integration test for the lexer, test all possible cases
    :return
    """
    lex.input(lex_test_all)

    while True:
        tok = lex.token()
        if not tok:
            break  # No more input
    pass


def test_example_6(lex):
    """
    Integration test for the lexer, test all possible cases
    :return:
    """
    lex.input(lex_example_6)
    while True:
        tok = lex.token()
        if not tok:
            break  # No more input
    pass
