def test_if(lex):
    lex.input('if')
    tok = lex.token()
    assert str(tok.type) == 'IF'