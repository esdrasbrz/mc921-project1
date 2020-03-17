import lex.calculator_example
import lex.lexer


def test_calculator_example():
    lexer = lex.calculator_example.lexer
    # Test it out
    data = '''
    3 + 4 * 10
    + -20 *2
    '''
    # Give the lexer some input
    lexer.input(data)

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break      # No more input
        print(tok)
    pass


def test_lexer():
    lexer = lex.lexer.lexer  # will fix this later, my bad

    data = '''
    _int = 333
    float1 = 444.4
    string = "Hello World\n" 
    // test inline comment
    /* test block comment */
    
    '''
    lexer.input(data)

    while True:
        tok = lexer.token()
        if not tok:
            break      # No more input
        print(tok)
    pass


if __name__ == "__main__":
    print('\n=== test_calculator_example() ===\n')
    test_calculator_example()
    print('\n=== test_lexer() ===\n')
    test_lexer()
