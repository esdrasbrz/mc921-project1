from ply.yacc import yacc

from . import ast_classes
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
        return ast_classes.Coord(p.lineno(token_idx), column)

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
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'EQUAL', 'DIFFERENT'),
        ('left', 'BIGGER', 'BIGGER_EQUAL', 'SMALLER', 'SMALLER_EQUAL'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE', 'MOD')
        )

    def p_program(self, p):
        """ program  : global_declaration_list
        """
        coord = self._token_coord(p,1)
        p[0] = ast_classes.Program(p[1], coord)

    def p_global_declaration_list(self, p):
        """ global_declaration_list : global_declaration
                                    | global_declaration_list global_declaration
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    # This is not right, just a workaround to make the compiler work
    def p_global_declaration(self, p):
        """ global_declaration : constant_expression
        """
        p[0] = p[1]

    def p_jump_statement_1(self, p):
        """ jump_statement  : BREAK SEMI
        """
        p[0] = ast_classes.Break(self._token_coord(p, 1))

    def p_jump_statement_2(self, p):
        """ jump_statement  : RETURN expression_opt SEMI
        """
        p[0] = ast_classes.Return(p[2] if len(p) == 4 else None, self._token_coord(p, 1))

    def p_postfix_expression_1(self, p):
        """ postfix_expression : primary_expression
        """
        p[0] = p[1]

    def p_block_item(self, p):
        """ block_item  : declaration
                        | statement
        """
        if isinstance(p[1], list):
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_block_item_list(self, p):
        """ block_item_list : block_item
                            | block_item_list block_item
        """
        if len(p) == 2 or p[2] == [None]:
            p[0] = p[1]
        else:
            p[0] = p[1] + p[2]

    def p_compound_statement(self, p):
        """compound_statement   : LBRACES block_item_list RBRACES
        """
        p[0] = ast_classes.Compound(block_items=p[2], coord=self._token_coord(p, 1))

    def p_selection_statement_1(self, p):
        """ selection_statement : IF LPAREN expression RPAREN statement
        """
        p[0] = ast_classes.If(p[3], p[5], None, self._token_coord(p, 1))

    def p_selection_statement_2(self, p):
        """ selection_statement : IF LPAREN expression RPAREN statement ELSE statement
        """
        p[0] = ast_classes.If(p[3], p[5], p[7], self._token_coord(p, 1))

    def p_iteration_statement_1(self, p):
        """ iteration_statement : WHILE LPAREN expression RPAREN statement
        """
        p[0] = ast_classes.While(p[3], p[5], self._token_coord(p, 1))

    def p_iteration_statement_2(self, p):
        """ iteration_statement : FOR LPAREN expression_opt SEMI expression_opt SEMI expression_opt RPAREN statement
        """
        p[0] = ast_classes.For(p[3], p[5], p[7], p[9], self._token_coord(p, 1))

    def p_iteration_statement_3(self, p):
        """ iteration_statement : FOR LPAREN declaration expression_opt SEMI expression_opt RPAREN statement
        """
        p[0] = ast_classes.For(ast_classes.DeclList(p[3], self._token_coord(p, 1)),
                         p[4], p[6], p[8], self._token_coord(p, 1))

    def p_expression_statement(self, p):
        """ expression_statement : expression_opt SEMI
        """
        if p[1] is None:
            p[0] = ast_classes.EmptyStatement(self._token_coord(p, 2))
        else:
            p[0] = p[1]

    def p_assert_statement(self, p):
        """ assert_statement : ASSERT expression SEMI
        """
        p[0] = ast_classes.Assert(p[1])

    def p_print_statement(self, p):
        """ print_statement : PRINT LPAREN expression_opt RPAREN SEMI
        """
        p[0] = ast_classes.Print(p[2])

    def p_read_statement(self, p):
        """ read_statement : READ LPAREN argument_expression RPAREN SEMI
        """
        p[0] = ast_classes.Read(p[2])

    def p_statement(self, p):
        """ statement   : expression_statement
                        | compound_statement
                        | selection_statement
                        | iteration_statement
                        | jump_statement
                        | assert_statement
                        | print_statement
                        | read_statement
        """
        p[0] = p[1]

    def p_postfix_expression_2(self, p):
        """ postfix_expression : postfix_expression PLUS_PLUS
                               | postfix_expression MINUS_MINUS
        """
        p[0] = ast_classes.UnaryOp(p[2], p[1], p[1].coord)

    def p_postfix_expression_3(self, p):
        """ postfix_expression  : postfix_expression LPAREN RPAREN
                                | postfix_expression LPAREN argument_expression RPAREN
                                | postfix_expression LBRACKET expression RBRACKET
        """
        p[0] = ast_classes.FuncCall(p[1], p[3] if len(p) == 5 else None, p[1].coord)

    def p_argument_expression(self, p):
        """ argument_expression : assignment_expression
                                | argument_expression COMMA assignment_expression
        """
        if len(p) == 2: # single expr
            p[0] = ast_classes.ExprList([p[1]], p[1].coord)
        else:
            p[1].exprs.append(p[3])
            p[0] = p[1]

    def p_empty(self, p):
        """empty : """
        pass

    def p_expression_opt(self, p):
        """ expression_opt : expression
                           | empty
        """
        p[0] = p[1]

    def p_expression_1(self, p):
        """ expression  : assignment_expression
        """
        p[0] = p[1]

    def p_expression_2(self, p):
        """ expression  : expression COMMA assignment_expression
        """
        if not isinstance(p[1], ast_classes.ExprList):
            p[1] = ast_classes.ExprList(p[1], p[1].coord)
        p[1].exprs.append(p[3])
        p[0] = p[1]


    def p_primary_expression_1(self, p):
        """ primary_expression : identifier
                               | constant
        """
        p[0] = p[1]

    def p_primary_expression_2(self, p):
        """ primary_expression : LPAREN expression RPAREN
        """
        p[0] = p[2]

    def p_cast_expression_1(self, p):
        """ cast_expression : postfix_expression
        """
        p[0] = p[1]

    def p_cast_expression_2(self, p):
        """ cast_expression : LPAREN type_specifier RPAREN cast_expression
        """
        p[0] = ast_classes.Cast(p[2], p[4], self._token_coord(p, 1))

    def p_assignment_expression(self, p):
        """ assignment_expression   : binary_expression
                                    | unary_expression assignment_operator assignment_expression
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast_classes.Assignment(p[2], p[1], p[3], p[1].coord)

    def p_assignment_operator(self, p):
        """ assignment_operator : ASSIGN
                                | ASSIGN_TIMES
                                | ASSIGN_DIVIDE
                                | ASSIGN_MOD
                                | ASSIGN_PLUS
                                | ASSIGN_MINUS
        """
        p[0] = p[1]

    def p_unary_expression_1(self, p):
        """ unary_expression : postfix_expression
        """
        p[0] = p[1]

    def p_unary_expression_2(self, p):
        """ unary_expression    : PLUS_PLUS unary_expression
                                | MINUS_MINUS unary_expression
                                | unary_operator cast_expression
        """
        p[0] = ast_classes.UnaryOp(p[1], p[2], p[2].coord)

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
            p[0] = ast_classes.BinaryOp(p[2], p[1], p[3], p[1].coord)

    def p_constant_expression(self, p):
        """ constant_expression : binary_expression
        """
        p[0] = p[1]

    def p_identifier(self, p):
        """ identifier : ID
        """
        coord = self._token_coord(p,1)
        p[0] = ast_classes.ID(p[1], coord)

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
        p[0] = ast_classes.Type([p[1]], coord)

    def p_constant_1(self, p):
        """ constant : INT_CONST
        """
        coord = self._token_coord(p,1)
        p[0] = ast_classes.Constant('int', p[1], coord)

    def p_constant_2(self, p):
        """ constant : FLOAT_CONST
        """
        coord = self._token_coord(p,1)
        p[0] = ast_classes.Constant('float', p[1], coord)

    def p_constant_3(self, p):
        """ constant : STRING_CONST
        """
        coord = self._token_coord(p,1)
        p[0] = ast_classes.Constant('string', p[1], coord)

    def p_declarator(self, p):
        """ declarator  : direct_declarator
        """
        p[0] = p[1]

    def p_direct_declarator_1(self, p):
        """ direct_declarator   : identifier
        """
        p[0] = p[1]

    def p_direct_declarator_2(self, p):
        """ direct_declarator   : LPAREN declarator RPAREN
        """

    def p_direct_declarator_3(self, p):
        """ direct_declarator   : direct_declarator LBRACKET LBRACES constant_expression RBRACES QUESTION RBRACKET
        """

    def p_direct_declarator_4(self, p):
        """ direct_declarator   : direct_declarator LPAREN parameter_list RPAREN
        """

    def p_direct_declarator_5(self, p):
        """ direct_declarator   : direct_declarator LPAREN LBRACES identifier RBRACES TIMES RPAREN
        """

    def p_error (self, p):
        if p:
            print("Error near the symbol %s" % p.value)
        else:
            print("Error at the end of input")
