from ply.yacc import yacc

from .ast_classes import *
from .lex.uc_lexer import UCLexer

def print_error(msg, x, y):
    print("Lexical error: %s at %d:%d" % (msg, x, y))

class UCParser:
    tokens = UCLexer.tokens

    def __init__(self):
        self.lexer = UCLexer(print_error)
        self.lexer.build()
        self.parser = yacc(module=self)
        pass

    def parse(self, text, filename='', debug=False):
        """ Parses uC code and returns an AST.
            text:
                A string containing the uC source code
            filename:
                Name of the file being parsed (for meaningful
                error messages)
        """
        return self.parser.parse(
                input=text,
                lexer=self.lexer,
                debug=debug)

    precedence = (
        ('left', 'PLUS'),
        ('left', 'TIMES')
        )

    def p_program(self, p):
        """ program  : global_declaration_list
        """
        p[0] = Program(p[1])

    def p_global_declaration_list(self, p):
        """ global_declaration_list : global_declaration
                                    | global_declaration_list global_declaration
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_global_declaration(self, p):
        """ global_declaration : constant
        """
        p[0] = p[1]

    def p_constant_1(self, p):
        """ constant : INT_CONST
        """
        p[0] = Constant('int', p[1])

    def p_constant_2(self, p):
        """ constant : FLOAT_CONST
        """
        p[0] = Constant('float', p[1])

    def p_constant_3(self, p):
        """ constant : STRING_CONST
        """
        p[0] = Constant('string', p[1])

    def p_error (self, p):
        if p:
            print("Error near the symbol %s" % p.value)
        else:
            print("Error at the end of input")
