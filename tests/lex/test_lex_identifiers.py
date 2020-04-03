def test_ccomment(lex):
    lex.input('/* test block comment */')

    tok = lex.token()
    assert not tok


def test_unterminated_comment(lex):
    lex.input('/* incomplete block comment')

    tok = lex.token()
    pass


def test_unterminated_string(lex):
    lex.input('" incomplete single quote string')
    tok = lex.token()

    lex.input("' incomplete double quote string")
    tok = lex.token()
    pass



def test_ucomment(lex):
    lex.input('// test inline comment')

    tok = lex.token()
    assert not tok


def test_id(lex):
    lex.input('_int')
    tok = lex.token()
    assert tok.type == 'ID'
    assert tok.value == '_int'

    lex.input('_float1')
    tok = lex.token()
    assert tok.type == 'ID'
    assert tok.value == '_float1'

    lex.input('string')
    tok = lex.token()
    assert tok.type == 'ID'
    assert tok.value == 'string'


def test_newline(lex):
    lex.input('\n')
    tok = lex.token()
    assert not tok


def test_int_const(lex):
    lex.input('3412')
    tok = lex.token()
    assert tok.type == 'INT_CONST'
    assert tok.value == 3412


def test_float_const(lex):
    lex.input('222.4')
    tok = lex.token()
    assert tok.type == 'FLOAT_CONST'
    assert tok.value == 222.4

    lex.input('.4')
    tok = lex.token()
    assert tok.type == 'FLOAT_CONST'
    assert tok.value == 0.4


def test_string_const(lex):
    lex.input('"Hello World"')
    tok = lex.token()
    assert tok.type == 'STRING_CONST'
    assert tok.value == '"Hello World"'

