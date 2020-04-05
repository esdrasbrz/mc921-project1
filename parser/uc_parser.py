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

    def _token_coord(self, p, token_idx):
        last_cr = p.lexer.lexer.lexdata.rfind('\n', 0, p.lexpos(token_idx))
        if last_cr < 0:
            last_cr = -1
        column = (p.lexpos(token_idx) - (last_cr))
        return Coord(p.lineno(token_idx), column)

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
        coord = self._token_coord(p,1)
        p[0] = Program(p[1], coord)

    def p_global_declaration_list(self, p):
        """ global_declaration_list : global_declaration
                                    | global_declaration_list global_declaration
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    # This is not right, just a workaround to make the compiler work
    def p_global_declaration(self, p):
        """ global_declaration : postfix_expression
                               | type_specifier
                               | assignment_operator
                               | cast_expression
                               | unary_expression
        """
        p[0] = p[1]

    def p_postfix_expression_1(self, p):
        """ postfix_expression : primary_expression
        """
        p[0] = p[1]

    def p_postfix_expression_2(self, p):
        """ postfix_expression : postfix_expression PLUS_PLUS
                            | postfix_expression MINUS_MINUS
        """
        p[0] = UnaryOp(p[2], p[1], p[1].coord)

    def p_primary_expression(self, p):
        """ primary_expression : identifier
                               | constant
        """
        p[0] = p[1]

    def p_cast_expression_1(self, p):
        """ cast_expression : postfix_expression
        """
        p[0] = p[1]

    def p_cast_expression_2(self, p):
        """ cast_expression : LPAREN type_specifier RPAREN cast_expression
        """
        p[0] = Cast(p[2], p[4], self._token_coord(p, 1))

    def p_unary_expression_1(self, p):
        """ unary_expression : postfix_expression
        """
        p[0] = p[1]

    def p_unary_expression_2(self, p):
        """ unary_expression    : PLUS_PLUS unary_expression
                                | MINUS_MINUS unary_expression
                                | unary_operator cast_expression
        """
        p[0] = UnaryOp(p[1], p[2], p[2].coord)

    def p_binary_expression(self, p):
        """ binary_expression   : cast_expression
                                | binary_expression TIMES binary_expression
                                | binary_expression DIVIDE binary_expression
                                | binary_expression MOD binary_expression
                                | binary_expression PLUS binary_expression
                                | binary_expression MINUS binary_expression
                                | binary_expression SMALLER binary_expression
                                | binary_expression SMALLER_EQUAL binary_expression
                                | binary_expression BIGGER binary_expression
                                | binary_expression BIGGER_EQUAL binary_expression
                                | binary_expression EQUAL binary_expression
                                | binary_expression DIFFERENT binary_expression
                                | binary_expression AND binary_expression
                                | binary_expression OR binary_expression
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)

    def p_constant_expression(self, p):
        """ constant_expression    : binary_expression
        """
        p[0] = p[1]

    def p_identifier(self, p):
        """ identifier  : ID
        """
        coord = self._token_coord(p,1)
        p[0] = ID(p[1], coord)

    def p_unary_operator(self, p):
        """ unary_operator : UPPERSAND
                           | TIMES
                           | PLUS
                           | MINUS
                           | NOT
        """
        p[0] = p[1]

    def p_type_specifier(self, p):
        """ type_specifier : VOID
                           | CHAR
                           | INT
                           | FLOAT
        """
        coord = self._token_coord(p,1)
        p[0] = Type([p[1]], coord)

    def p_assignment_operator(self, p):
        """ assignment_operator : ASSIGN
                                | ASSIGN_TIMES
                                | ASSIGN_DIVIDE
                                | ASSIGN_REMAINDER
                                | ASSIGN_PLUS
                                | ASSIGN_MINUS
        """
        coord = self._token_coord(p,1)
        p[0] = Assignment(p[1], coord)

    def p_constant_1(self, p):
        """ constant : INT_CONST
        """
        coord = self._token_coord(p,1)
        p[0] = Constant('int', p[1], coord)

    def p_constant_2(self, p):
        """ constant : FLOAT_CONST
        """
        coord = self._token_coord(p,1)
        p[0] = Constant('float', p[1], coord)

    def p_constant_3(self, p):
        """ constant : STRING_CONST
        """
        coord = self._token_coord(p,1)
        p[0] = Constant('string', p[1], coord)

    def p_error (self, p):
        if p:
            print("Error near the symbol %s" % p.value)
        else:
            print("Error at the end of input")
