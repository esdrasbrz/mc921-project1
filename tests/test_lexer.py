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

    tok = lex.token()
    assert not tok


def test_ucomment(lex):
    lex.input('// test inline comment')

    tok = lex.token()
    assert not tok


def test_id(lex):
    lex.input('_int')
    tok = lex.token()
    assert str(tok) == "LexToken(ID,'_int',8,0)"

    lex.input('_float1')
    tok = lex.token()
    assert str(tok) == "LexToken(ID,'_float1',8,0)"

    lex.input('string')
    tok = lex.token()
    assert str(tok) == "LexToken(ID,'string',8,0)"


def test_newline(lex):
    lex.input('\n')
    tok = lex.token()
    assert not tok


def test_int_const(lex):
    lex.input('3412')
    tok = lex.token()
    assert str(tok) == 'LexToken(INT_CONST,3412,9,0)'


def test_string_const(lex):
    lex.input('"Hello World"')
    tok = lex.token()
    assert str(tok) == 'LexToken(STRING_CONST,\'"Hello World"\',9,0)'

