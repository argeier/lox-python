from typing import List

from .error_handler import ErrorHandler, ParseError
from .expr import (
    Assign,
    Binary,
    Call,
    Expr,
    Get,
    Grouping,
    Literal,
    Logical,
    Set,
    Super,
    Conditional,
    This,
    Unary,
    Variable,
)
from .stmt import (
    Block,
    Break,
    Class,
    Expression,
    Function,
    If,
    Print,
    Return,
    Stmt,
    Trait,
    Var,
    While,
)
from .tokens import Token, TokenType


class Parser:

    def __init__(
        self, tokens: List[Token], error_handler: ErrorHandler = ErrorHandler()
    ):
        self.tokens: List[Token] = tokens
        self.current: int = 0
        self.error_handler: ErrorHandler = error_handler

    def parse(self) -> List[Stmt]:
        statements: List[Stmt] = []
        while not self._is_at_end():
            stmt = self._declaration()
            assert stmt is not None
            statements.append(stmt)

        return statements

    def _declaration(self) -> Stmt | None:
        try:
            if self._match(TokenType.CLASS):
                return self._class_declaration()
            if self._match(TokenType.TRAIT):
                return self._trait_declaration()
            if self._match(TokenType.FUN):
                return self._function("function")
            if self._match(TokenType.VAR):
                return self._var_declaration()
            return self._statement()
        except ParseError:
            self._synchronize()
            return None

    def _class_declaration(self) -> Class:
        name: Token = self._consume(TokenType.IDENTIFIER, "Expect class name.")

        methods: List[Function] = []
        class_methods: List[Function] = []

        superclass: Variable | None = None
        if self._match(TokenType.LESS):
            self._consume(TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = Variable(self._previous())

        traits: List[Expr] = self._with_clause()

        self._consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            is_class_method: bool = self._match(TokenType.CLASS)
            (class_methods if is_class_method else methods).append(
                self._function("method")
            )

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")

        return Class(name, superclass, methods, class_methods, traits)

    def _trait_declaration(self) -> Trait:
        name: Token = self._consume(TokenType.IDENTIFIER, "Expect trait name.")
        traits: List[Expr] = self._with_clause()

        self._consume(TokenType.LEFT_BRACE, "Expect '{' before trait body.")

        methods: List[Function] = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            methods.append(self._function("method"))

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after trait body.")

        return Trait(name, traits, methods)

    def _with_clause(self) -> List[Expr]:
        traits: List[Expr] = []
        if self._match(TokenType.WITH):
            while True:
                self._consume(TokenType.IDENTIFIER, "Expect trait name.")
                traits.append(Variable(self._previous()))
                if not self._match(TokenType.COMMA):
                    break
        return traits

    def _var_declaration(self) -> Var:
        name: Token = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer: Expr | None = None
        if self._match(TokenType.EQUAL):
            initializer_expr = self._expression()
            if initializer_expr is None:
                raise self.error_handler.parse_error(
                    token=self._peek(), message="Expected expression after '='."
                )
            initializer = initializer_expr
        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        # Create empty Literal if initializer is None
        return Var(name, initializer if initializer is not None else Literal(None))

    def _statement(self) -> Stmt:
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.FOR):
            return self._for_statement()
        if self._match(TokenType.PRINT):
            return self._print_statement()
        if self._match(TokenType.RETURN):
            return self._return_statement()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.BREAK):
            return self._break_statement()
        if self._match(TokenType.LEFT_BRACE):
            return Block(self._block())
        return self._expression_statement()

    def _block(self) -> List[Stmt]:
        statements: List[Stmt] = []

        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            stmt = self._declaration()
            assert stmt is not None
            statements.append(stmt)

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def _print_statement(self) -> Print:
        value: Expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def _if_statement(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition: Expr = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch: Stmt = self._statement()
        else_branch: Stmt | None = None

        if self._match(TokenType.ELSE):
            else_branch = self._statement()

        return If(condition, then_branch, else_branch)

    def _for_statement(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer: Stmt | None = None
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()

        condition: Expr | None = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment: Expr | None = None
        if not self._check(TokenType.RIGHT_PAREN):
            increment = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body: Stmt = self._statement()

        if increment is not None:
            body = Block([body, Expression(increment)])

        if condition is None:
            condition = Literal(True)
        body = While(condition, body)

        if initializer is not None:
            body = Block([initializer, body])

        return body

    def _while_statement(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition: Expr = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after while condition.")
        body: Stmt = self._statement()
        return While(condition, body)

    def _break_statement(self) -> Stmt:
        self._consume(TokenType.SEMICOLON, "Expect ';' after 'break'.")
        return Break()

    def _expression_statement(self) -> Expression:
        expr: Expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after _expression.")
        return Expression(expr)

    def _return_statement(self) -> Stmt:
        keyword: Token = self._previous()
        value: Expr | None = None
        if not self._check(TokenType.SEMICOLON):
            value = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)

    def _function(self, kind: str) -> Function:
        """Parse a function declaration and return a Function statement node."""
        name: Token = self._consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        parameters: List[Token] | None = None

        if kind != "method" or self._check(TokenType.LEFT_PAREN):
            self._consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
            parameters = []

            if not self._check(TokenType.RIGHT_PAREN):
                while True:
                    if len(parameters) >= 255:
                        self.error(self._peek(), "Can't have more than 255 parameters.")

                    parameters.append(
                        self._consume(TokenType.IDENTIFIER, "Expect parameter name.")
                    )

                    if not self._match(TokenType.COMMA):
                        break

            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")

        self._consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body: List[Stmt] = self._block()

        return Function(name, parameters, body)

    def _expression(self) -> Expr:
        return self._conditional()

    def _conditional(self) -> Expr:
        expr: Expr = self._assignment()

        if self._match(TokenType.QUESTION):
            then_branch: Expr = self._expression()
            self._consume(
                TokenType.COLON,
                "Expect ':' after then branch of conditional expression.",
            )
            else_branch: Expr = self._conditional()
            expr = Conditional(expr, then_branch, else_branch)

        return expr

    def _assignment(self) -> Expr:
        expr: Expr = self._or()

        if self._match(TokenType.EQUAL):
            equals: Token = self._previous()
            value: Expr = self._assignment()

            if isinstance(expr, Variable):
                name: Token = expr.name
                return Assign(name, value)
            elif isinstance(expr, Get):
                get: Get = expr
                return Set(get.object, get.name, value)

            self.error_handler.parse_error(equals, "Invalid assignment target.")

        return expr

    def _or(self) -> Expr:
        expr: Expr = self._and()

        while self._match(TokenType.OR):
            operator: Token = self._previous()
            right: Expr = self._and()
            expr = Logical(expr, operator, right)

        return expr

    def _and(self) -> Expr:
        expr: Expr = self._equality()

        while self._match(TokenType.AND):
            operator: Token = self._previous()
            right: Expr = self._equality()
            expr = Logical(expr, operator, right)

        return expr

    def _equality(self) -> Expr:
        expr: Expr = self._comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self._previous()
            right: Expr = self._comparison()
            expr = Binary(expr, operator, right)

        return expr

    def _comparison(self) -> Expr:
        expr: Expr = self._term()

        while self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator: Token = self._previous()
            right: Expr = self._term()
            expr = Binary(expr, operator, right)

        return expr

    def _term(self) -> Expr:
        expr: Expr = self._factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self._previous()
            right: Expr = self._factor()
            expr = Binary(expr, operator, right)

        return expr

    def _factor(self) -> Expr:
        expr: Expr = self._unary()

        while self._match(TokenType.SLASH, TokenType.STAR, TokenType.MODULO):
            operator: Token = self._previous()
            right: Expr = self._unary()
            expr = Binary(expr, operator, right)

        return expr

    def _unary(self) -> Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self._previous()
            right: Expr = self._unary()
            return Unary(operator, right)

        return self._call()

    def _call(self) -> Expr:
        expr: Expr = self._primary()

        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            elif self._match(TokenType.DOT):
                name: Token = self._consume(
                    TokenType.IDENTIFIER, "Expect property name after '.'."
                )
                expr = Get(expr, name)
            else:
                break

        return expr

    def _finish_call(self, callee: Expr) -> Expr:
        arguments: List[Expr] = []

        if not self._check(TokenType.RIGHT_PAREN):
            arguments.append(self._expression())
            while self._match(TokenType.COMMA):
                if len(arguments) >= 255:
                    self.error_handler.parse_error(
                        self._peek(), "Cannot have more than 255 arguments."
                    )
                arguments.append(self._expression())

        paren: Token = self._consume(
            TokenType.RIGHT_PAREN, "Expect ')' after arguments."
        )
        return Call(callee, paren, arguments)

    def _primary(self) -> Expr:
        if self._match(TokenType.FALSE):
            return Literal(False)
        elif self._match(TokenType.TRUE):
            return Literal(True)
        elif self._match(TokenType.NIL):
            return Literal(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)

        if self._match(TokenType.SUPER):
            keyword: Token = self._previous()
            self._consume(TokenType.DOT, "Expect '.' after 'super'.")
            method: Token = self._consume(
                TokenType.IDENTIFIER, "Expect superclass method name."
            )
            return Super(keyword, method)

        if self._match(TokenType.THIS):
            return This(self._previous())

        if self._match(TokenType.IDENTIFIER):
            return Variable(self._previous())

        if self._match(TokenType.LEFT_PAREN):
            expr: Expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after _expression.")
            return Grouping(expr)

        raise self.error_handler.parse_error(
            token=self._peek(), message="Expect _expression."
        )

    # Utility Methods
    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _check(self, type: TokenType) -> bool:
        return False if self._is_at_end() else self._peek().type == type

    def _match(self, *types: TokenType) -> bool:
        for type in types:
            if self._check(type):
                self._advance()
                return True
        return False

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _consume(self, type: TokenType, message: str) -> Token:
        if self._check(type):
            return self._advance()
        raise self.error_handler.parse_error(token=self._peek(), message=message)

    def _synchronize(self) -> None:
        self._advance()

        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return

            if self._peek().type in (
                TokenType.CLASS,
                TokenType.FUNCTION,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ):
                return

            self._advance()
