from typing import List

from error_handler import ErrorHandler, ParseError
from expr import Binary, Expr, Grouping, Literal, Unary, Variable, Assign
from stmt import Expression, Print, Stmt, Var, Block
from tokens import Token, TokenType


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
            statements.append(self._declaration())

        return statements

    def _declaration(self) -> Stmt | None:
        try:
            if self._match(TokenType.VAR):
                return self._var_declaration()
            return self._statement()
        except ParseError:
            self._synchronize()
            return None

    def _var_declaration(self) -> Var:
        name: Token = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer: Expr = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def _statement(self) -> Expression | Print | Block:
        if self._match(TokenType.PRINT):
            return self._print_statement()
        if self._match(TokenType.LEFT_BRACE):
            return Block(self._block())
        return self._expression_statement()

    def _block(self) -> List[Stmt]:
        statements: List[Stmt] = []

        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            statements.append(self._declaration())

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def _print_statement(self) -> Print:
        value: Expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def _expression_statement(self) -> Expression:
        expr: Expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after _expression.")
        return Expression(expr)

    def _expression(self) -> Expr:
        return self._assignment()

    def _assignment(self) -> Expr:
        expr: Expr = self._equality()

        if self._match(TokenType.EQUAL):
            equals: Token = self._previous()
            value: Expr = self._assignment()

            if isinstance(expr, Variable):
                name: Token = expr.name
                return Assign(name, value)

            self.error_handler.error(equals, "Invalid assignment target.")

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

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self._previous()
            right: Expr = self._unary()
            expr = Binary(expr, operator, right)

        return expr

    def _unary(self) -> Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self._previous()
            right: Expr = self._unary()
            return Unary(operator, right)

        return self._primary()

    def _primary(self) -> Expr:
        if self._match(TokenType.FALSE):
            return Literal(False)
        elif self._match(TokenType.TRUE):
            return Literal(True)
        elif self._match(TokenType.NIL):
            return Literal(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)

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
