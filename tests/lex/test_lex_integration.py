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