from tests.data import lex_test


def test_lexer(lex):
    """
    Integration test for the lexer
    :return:
    """
    lex.input(lex_test)

    while True:
        tok = lex.token()
        if not tok:
            break  # No more input
        print(tok)
    pass


def test_ccomment(lex):
    lex.input('/* test block comment */')

    while True:
        tok = lex.token()
        assert not tok

        if not tok:
            break  # No more input
    pass

