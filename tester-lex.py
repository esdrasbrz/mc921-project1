import lex.calculator_example


def main():
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


if __name__ == "__main__":
    main()
