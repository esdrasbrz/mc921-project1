from ply.yacc import yacc

import ast_classes
from uc_lexer import UCLexer


def print_error(msg, x, y):
    print("Lexical error: %s at %d:%d" % (msg, x, y))


class ParseError(Exception):
    pass


class UCParser:
    tokens = UCLexer.tokens

    def __init__(self):
        self.lexer = UCLexer(print_error)
        self.lexer.build()
        self.parser = yacc(module=self)
        pass

    def _token_coord(self, p, token_idx, set_column=False):
        last_cr = p.lexer.lexer.lexdata.rfind('\n', 0, p.lexpos(token_idx))
        if last_cr < 0:
            last_cr = -1
        column = (p.lexpos(token_idx) - (last_cr))
        return ast_classes.Coord(p.lineno(token_idx), 1 if set_column else column)

    def _type_modify_decl(self, decl, modifier):
        """ Tacks a type modifier on a declarator, and returns
            the modified declarator.
            Note: the declarator and modifier may be modified
        """
        modifier_head = modifier
        modifier_tail = modifier

        # The modifier may be a nested list. Reach its tail.
        while modifier_tail.type:
            modifier_tail = modifier_tail.type

        # If the decl is a basic type, just tack the modifier onto it
        if isinstance(decl, ast_classes.VarDecl):
            modifier_tail.type = decl
            return modifier
        else:
            # Otherwise, the decl is a list of modifiers. Reach
            # its tail and splice the modifier onto the tail,
            # pointing to the underlying basic type.
            decl_tail = decl

            while not isinstance(decl_tail.type, ast_classes.VarDecl):
                decl_tail = decl_tail.type

            modifier_tail.type = decl_tail.type
            decl_tail.type = modifier_head
            return decl

    def _fix_decl_name_type(self, decl, typename):
        """ Fixes a declaration. Modifies decl.
        """
        # Reach the underlying basic type
        type = decl
        while not isinstance(type, ast_classes.VarDecl):
            type = type.type

        decl.name = type.declname

        # The typename is a list of types. If any type in this
        # list isn't an Type, it must be the only
        # type in the list.
        # If all the types are basic, they're collected in the
        # Type holder.
        for tn in typename:
            if not isinstance(tn, ast_classes.Type):
                if len(typename) > 1:
                    self._parse_error(
                        "Invalid multiple types specified", tn.coord)
                else:
                    type.type = tn
                    return decl

        if not typename:
            # Functions default to returning int
            if not isinstance(decl.type, ast_classes.FuncDecl):
                self._parse_error("Missing type in declaration", decl.coord)
            type.type = ast_classes.Type(['int'], coord=decl.coord)
        else:
            # At this point, we know that typename is a list of Type
            # nodes. Concatenate all the names into a single list.
            type.type = ast_classes.Type(
                [typename.names[0]],
                coord=typename.coord)
        return decl

    def _build_declarations(self, spec, decls):
        """ Builds a list of declarations all sharing the given specifiers.
        """
        declarations = []

        for decl in decls:
            assert decl['decl'] is not None
            declaration = ast_classes.Decl(
                name=None,
                type=decl['decl'],
                init=decl.get('init'),
                coord=decl['decl'].coord)
            fixed_decl = self._fix_decl_name_type(declaration, spec)
            declarations.append(fixed_decl)

        return declarations

    def _build_function_definition(self, spec, decl, param_decls, body):
        """ Builds a function definition.
        """
        declaration = self._build_declarations(
            spec=spec,
            decls=[dict(decl=decl, init=None)],
        )[0]


        return ast_classes.FuncDef(
            spec,
            declaration,
            param_decls,
            body,
            decl.coord)

    def _parse_error(self, msg, coord):
        raise Exception("{}: {}".format(coord, msg))

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
        coord = self._token_coord(p, 1)
        p[0] = ast_classes.Program(p[1], coord)

    def p_global_declaration_list(self, p):
        """ global_declaration_list : global_declaration
                                    | global_declaration_list global_declaration
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    # This is not right, just a workaround to make the compiler work
    def p_global_declaration_1(self, p):
        """ global_declaration  : declaration
        """
        p[0] = ast_classes.GlobalDecl(p[1])

    def p_global_declaration_2(self, p):
        """ global_declaration  : function_definition
        """
        p[0] = p[1]

    def p_declaration(self, p):
        """ declaration : decl_body SEMI
        """
        p[0] = p[1]

    def p_declaration_list(self, p):
        """ declaration_list    : declaration
                                | declaration_list declaration
        """
        p[0] = p[1] if len(p) == 2 else p[1] + p[2]

    def p_declaration_list_opt(self, p):
        """ declaration_list_opt    : declaration_list
                                    | empty
        """
        p[0] = p[1]

    def p_decl_body(self, p):
        """ decl_body  : type_specifier init_declarator_list_opt
        """
        type_spec = p[1]
        decls = None
        if p[2] is not None:
            decls = self._build_declarations(
                type_spec,
                p[2]
            )
        p[0] = decls

    def p_pointer(self, p):
        """ pointer : TIMES
                    | TIMES pointer
        """
        coord = self._token_coord(p, 1)
        nested_type = ast_classes.PtrDecl(type=None, coord=coord)
        if len(p) > 2:
            tail_type = p[2]
            while tail_type.type is not None:
                tail_type = tail_type.type
            tail_type.type = nested_type
            p[0] = p[2]
        else:
            p[0] = nested_type

    def p_declarator(self, p):
        """ declarator  : direct_declarator
        """
        p[0] = p[1]

    def p_declarator_2(self, p):
        """ declarator : pointer direct_declarator
        """
        p[0] = self._type_modify_decl(p[2], p[1])

    # Returns a {decl=<declarator> : init=<initializer>} dictionary
    # If there's no initializer, uses None
    def p_init_declarator(self, p):
        """ init_declarator : declarator
                            | declarator ASSIGN initializer
        """
        p[0] = dict(decl=p[1], init=(p[3] if len(p) > 2 else None))

    def p_init_declarator_list(self, p):
        """ init_declarator_list    : init_declarator
                                    | init_declarator_list COMMA init_declarator
        """
        p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]

    def p_init_declarator_list_opt(self, p):
        """ init_declarator_list_opt    : init_declarator_list
                                        | empty
        """
        p[0] = p[1]

    def p_parameter_declaration(self, p):
        """ parameter_declaration  : type_specifier declarator
        """
        # Returns Decls
        p[0] = self._build_declarations(
            p[1],
            [dict(decl=p[2])])[0]

    def p_parameter_list(self, p):
        """ parameter_list  : parameter_declaration
                            | parameter_list COMMA parameter_declaration
        """
        if len(p) == 2:  # single parameter
            p[0] = ast_classes.ParamList([p[1]], p[1].coord)
        else:
            p[1].params.append(p[3])
            p[0] = p[1]


    def p_direct_declarator_1(self, p):
        """ direct_declarator : identifier
        """
        p[0] = ast_classes.VarDecl(p[1], None, self._token_coord(p, 1))

    def p_direct_declarator_2(self, p):
        """ direct_declarator :  LPAREN declarator RPAREN
        """
        p[0] = p[2]

    def p_direct_declarator_3(self, p):
        """ direct_declarator : direct_declarator LBRACKET constant_expression_opt RBRACKET
        """
        array = ast_classes.ArrayDecl(
            None, p[3] if len(p) > 4 else None, p[1].coord)
        p[0] = self._type_modify_decl(p[1], array)

    def p_direct_declarator_4(self, p):
        """ direct_declarator : direct_declarator LPAREN identifier_list_opt RPAREN
                              | direct_declarator LPAREN parameter_list RPAREN
        """
        func = ast_classes.FuncDecl(p[3], None, p[1].coord)
        p[0] = self._type_modify_decl(p[1], func)



    def p_initializer_1(self, p):
        """ initializer : assignment_expression
        """
        p[0] = p[1]

    def p_initializer_2(self, p):
        """ initializer : LBRACES initializer_list RBRACES
                        | LBRACES initializer_list COMMA RBRACES
        """
        if p[2] is None:
            p[0] = ast_classes.InitList([], self._token_coord(p, 1))
        else:
            p[0] = p[2]

    def p_initializer_list(self, p):
        """ initializer_list : initializer
                             | initializer_list COMMA initializer
        """
        if len(p) == 2:  # single initializer
            p[0] = ast_classes.InitList([p[1]], p[1].coord)
        else:
            p[1].exprs.append(p[3])
            p[0] = p[1]

    def p_postfix_expression_1(self, p):
        """ postfix_expression : primary_expression
        """
        p[0] = p[1]

    def p_postfix_expression_2(self, p):
        """ postfix_expression : postfix_expression PLUS_PLUS
                               | postfix_expression MINUS_MINUS
        """
        p[0] = ast_classes.UnaryOp('p' + p[2], p[1], p[1].coord)

    def p_postfix_expression_3(self, p):
        """ postfix_expression  : postfix_expression LPAREN RPAREN
                                | postfix_expression LPAREN argument_expression RPAREN
        """
        p[0] = ast_classes.FuncCall(
            p[1], p[3] if len(p) > 4 else None, p[1].coord)

    def p_postfix_expression_4(self, p):
        """ postfix_expression  : postfix_expression LBRACKET expression RBRACKET
        """
        p[0] = ast_classes.ArrayRef(p[1], p[3], p[1].coord)

    def p_argument_expression(self, p):
        """ argument_expression : assignment_expression
                                | argument_expression COMMA assignment_expression
        """
        if len(p) == 2:  # single expr
            p[0] = p[1]
        else:
            if (not isinstance(p[1], ast_classes.ExprList)):
                p[1] = ast_classes.ExprList([p[1]], p[1].coord)
            p[1].exprs.append(p[3])
            p[0] = p[1]

    def p_expression_1(self, p):
        """ expression  : assignment_expression
        """
        p[0] = p[1]

    def p_expression_2(self, p):
        """ expression  : expression COMMA assignment_expression
        """
        if not isinstance(p[1], ast_classes.ExprList):
            p[1] = ast_classes.ExprList([p[1]], p[1].coord)
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
        """ cast_expression : unary_expression
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

    def p_constant_expression_opt(self, p):
        """ constant_expression_opt : constant_expression
                                    | empty
        """
        p[0] = p[1]

    def p_identifier(self, p):
        """ identifier : ID
        """
        coord = self._token_coord(p, 1)
        p[0] = ast_classes.ID(p[1], coord)

    def p_identifier_list_opt(self, p):
        """ identifier_list_opt : identifier_list
                                | empty
        """
        p[0] = p[1]

    def p_identifier_list(self, p):
        """ identifier_list : identifier
                            | identifier_list COMMA identifier
        """
        if len(p) == 2:  # single parameter
            p[0] = ast_classes.ParamList([p[1]], p[1].coord)
        else:
            p[1].params.append(p[3])
            p[0] = p[1]

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
        coord = self._token_coord(p, 1)
        p[0] = ast_classes.Type([p[1]], coord)

    def p_constant_1(self, p):
        """ constant : INT_CONST
        """
        coord = self._token_coord(p, 1)
        p[0] = ast_classes.Constant('int', p[1], coord)

    def p_constant_2(self, p):
        """ constant : FLOAT_CONST
        """
        coord = self._token_coord(p, 1)
        p[0] = ast_classes.Constant('float', p[1], coord)

    def p_constant_3(self, p):
        """ constant : STRING_CONST
        """
        coord = self._token_coord(p, 1)
        p[0] = ast_classes.Constant('string', p[1], coord)

    def p_jump_statement_1(self, p):
        """ jump_statement  : BREAK SEMI
        """
        p[0] = ast_classes.Break(self._token_coord(p, 1))

    def p_jump_statement_2(self, p):
        """ jump_statement  : RETURN expression_opt SEMI
        """
        p[0] = ast_classes.Return(p[2] if len(p) == 4 else None, self._token_coord(p, 1))

    def p_block_item(self, p):
        """ block_item  : declaration
                        | statement
        """
        p[0] = p[1] if isinstance(p[1], list) else [p[1]]

    def p_block_item_list(self, p):
        """ block_item_list : block_item
                            | block_item_list block_item
        """
        p[0] = p[1] if len(p) == 2 or p[2] == [None] else p[1] + p[2]

    def p_compound_statement(self, p):
        """ compound_statement   : LBRACES block_item_list RBRACES
        """
        p[0] = ast_classes.Compound(block_items=p[2], coord=self._token_coord(p, 1, set_column=True))

    def p_selection_statement_1(self, p):
        """ selection_statement : IF LPAREN expression RPAREN statement
        """
        p[0] = ast_classes.If(p[3], p[5], None, self._token_coord(p, 1))
        # This is only needed because of professor's mistake dealing with cols

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
        p[0] = ast_classes.Assert(p[2], self._token_coord(p, 1))

    def p_print_statement(self, p):
        """ print_statement : PRINT LPAREN expression_opt RPAREN SEMI
        """
        p[0] = ast_classes.Print(p[3], self._token_coord(p, 1))

    def p_read_statement(self, p):
        """ read_statement : READ LPAREN argument_expression RPAREN SEMI
        """
        p[0] = ast_classes.Read(p[3], self._token_coord(p, 1))

    def p_statement(self, p):
        """ statement   : expression_statement
                        | selection_statement
                        | compound_statement
                        | iteration_statement
                        | jump_statement
                        | assert_statement
                        | print_statement
                        | read_statement
        """
        p[0] = p[1]

    def p_expression_opt(self, p):
        """ expression_opt : expression
                           | empty
        """
        p[0] = p[1]

    def p_function_definition_1(self, p):
        """ function_definition : type_specifier declarator declaration_list_opt compound_statement
        """
        spec = p[1]

        p[0] = self._build_function_definition(spec, p[2], p[3], p[4])

    def p_function_definition_2(self, p):
        """ function_definition : declarator declaration_list_opt compound_statement
        """
        spec = dict(
            type=[ast_classes.Type(['void'],
            coord=self._token_coord(p, 1))],
            function=[])

        p[0] = self._build_function_definition(spec, p[1], p[2], p[3])

    def p_empty(self, p):
        """ empty :
        """
        pass

    def p_error(self, p):
        if p:
            print("Error near the symbol %s" % p.value)
        else:
            print("Error at the end of input")
