lex_identifier_test = '''
_int = 333
float1 = 444.4
string = "Hello World\n"
// test inline comment
/* test block comment */
/* "This is a string inside a block comment" */
'''

lex_reserved_test = '''
if void else char for break
while float assert int
print read return
'''

lex_test_all = '''
// test inline comment
if void else char for break

/* test block comment */
/* "This is a string inside a block comment" */
_int = 333
float1 = 444.4
string = "Hello World\n"

while float assert int
print read return
'''

def test_lex_identifiers(lex):
    """
    Integration test for the lex, tests identifiers
    :return:
    """
    lex.input(lex_identifier_test)

    while True:
        tok = lex.token()
        if not tok:
            break  # No more input
        print(tok)
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
        print(tok)
    pass

def test_lex_all(lex):
    """
    Integration test for the lexer, test all possible cases
    :return:
    """
    lex.input(lex_test_all)

    while True:
        tok = lex.token()
        if not tok:
            break  # No more input
        print(tok)
    pass
