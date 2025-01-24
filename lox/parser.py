from __future__ import annotations

from typing import List, Optional, TypeVar

from .error_handler import ErrorHandler, ParseError
from .expr import (
    Assign,
    Binary,
    Call,
    Conditional,
    Expr,
    Get,
    Grouping,
    Literal,
    Logical,
    Set,
    Super,
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

T = TypeVar("T")


class Parser:
    """
    Parses a list of tokens into an Abstract Syntax Tree (AST) consisting of statements.

    Attributes:
        tokens (List[Token]): The list of tokens to parse.
        current (int): The current position in the tokens list.
        error_handler (ErrorHandler): Handles parsing errors.
    """

    __slots__ = ("tokens", "current", "error_handler")

    def __init__(
        self, tokens: List[Token], error_handler: Optional[ErrorHandler] = None
    ) -> None:
        self.tokens: List[Token] = tokens
        self.current: int = 0
        self.error_handler: ErrorHandler = (
            error_handler if error_handler else ErrorHandler()
        )

    def parse(self) -> List[Stmt]:
        """
        Parses the tokens into a list of statement nodes.

        Returns:
            List[Stmt]: The list of parsed statements.
        """
        statements: List[Stmt] = []
        while not self._is_at_end():
            stmt = self._declaration()
            if stmt is not None:
                statements.append(stmt)
        return statements

    def _declaration(self) -> Optional[Stmt]:
        """
        Parses a declaration statement.

        Returns:
            Optional[Stmt]: The parsed statement or None if an error occurred.
        """
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

    def _class_declaration(self) -> Optional[Class]:
        """
        Parses a class declaration.

        Returns:
            Optional[Class]: The parsed class statement.
        """
        name: Token = self._consume(TokenType.IDENTIFIER, "Expect class name.")

        superclass: Optional[Variable] = None
        if self._match(TokenType.LESS):
            self._consume(TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = Variable(self._previous())

        traits: List[Expr] = self._with_clause()

        self._consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods: List[Function] = []
        class_methods: List[Function] = []

        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            is_class_method: bool = self._match(TokenType.CLASS)
            (class_methods if is_class_method else methods).append(
                self._function("method")
            )

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")

        return Class(name, superclass, methods, class_methods, traits)

    def _trait_declaration(self) -> Trait:
        """
        Parses a trait declaration.

        Returns:
            Trait: The parsed trait statement.
        """
        name: Token = self._consume(TokenType.IDENTIFIER, "Expect trait name.")
        traits: List[Expr] = self._with_clause()

        self._consume(TokenType.LEFT_BRACE, "Expect '{' before trait body.")

        methods: List[Function] = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            methods.append(self._function("method"))

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after trait body.")

        return Trait(name, traits, methods)

    def _with_clause(self) -> List[Expr]:
        """
        Parses the 'with' clause for traits.

        Returns:
            List[Expr]: The list of traits used.
        """
        traits: List[Expr] = []
        if self._match(TokenType.WITH):
            while True:
                self._consume(TokenType.IDENTIFIER, "Expect trait name.")
                traits.append(Variable(self._previous()))
                if not self._match(TokenType.COMMA):
                    break
        return traits

    def _var_declaration(self) -> Var:
        """
        Parses a variable declaration.

        Returns:
            Var: The parsed variable declaration statement.
        """
        name: Token = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer: Optional[Expr] = None
        if self._match(TokenType.EQUAL):
            initializer_expr = self._expression()
            if initializer_expr is None:
                raise self.error_handler.parse_error(
                    token=self._peek(), message="Expected expression after '='."
                )
            initializer = initializer_expr
        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer if initializer is not None else Literal(None))

    def _statement(self) -> Stmt:
        """
        Parses a single statement.

        Returns:
            Stmt: The parsed statement.
        """
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
        """
        Parses a block of statements enclosed in braces.

        Returns:
            List[Stmt]: The list of parsed statements within the block.
        """
        statements: List[Stmt] = []

        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            stmt = self._declaration()
            if stmt is not None:
                statements.append(stmt)

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def _print_statement(self) -> Print:
        """
        Parses a print statement.

        Returns:
            Print: The parsed print statement.
        """
        value: Expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def _if_statement(self) -> If:
        """
        Parses an if statement.

        Returns:
            If: The parsed if statement.
        """
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition: Expr = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch: Stmt = self._statement()
        else_branch: Optional[Stmt] = None

        if self._match(TokenType.ELSE):
            else_branch = self._statement()

        return If(condition, then_branch, else_branch)

    def _for_statement(self) -> Stmt:
        """
        Parses a for statement and desugars it into a while loop.

        Returns:
            Stmt: The desugared while loop statement.
        """
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer: Optional[Stmt] = None
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()

        condition: Optional[Expr] = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment: Optional[Expr] = None
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

    def _while_statement(self) -> While:
        """
        Parses a while loop statement.

        Returns:
            While: The parsed while loop statement.
        """
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition: Expr = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after while condition.")
        body: Stmt = self._statement()
        return While(condition, body)

    def _break_statement(self) -> Break:
        """
        Parses a break statement.

        Returns:
            Break: The parsed break statement.
        """
        self._consume(TokenType.SEMICOLON, "Expect ';' after 'break'.")
        return Break()

    def _expression_statement(self) -> Expression:
        """
        Parses an expression statement.

        Returns:
            Expression: The parsed expression statement.
        """
        expr: Expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)

    def _return_statement(self) -> Return:
        """
        Parses a return statement.

        Returns:
            Return: The parsed return statement.
        """
        keyword: Token = self._previous()
        value: Optional[Expr] = None
        if not self._check(TokenType.SEMICOLON):
            value = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)

    def _function(self, kind: str) -> Function:
        """
        Parses a function declaration.

        Args:
            kind (str): The kind of function being parsed (e.g., "function", "method").

        Returns:
            Function: The parsed function declaration statement.
        """
        name: Token = self._consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        parameters: Optional[List[Token]] = None

        if kind != "method" or self._check(TokenType.LEFT_PAREN):
            self._consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
            parameters = []

            if not self._check(TokenType.RIGHT_PAREN):
                while True:
                    if len(parameters) >= 255:
                        self.error_handler.error(
                            self._peek(), "Can't have more than 255 parameters."
                        )

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
        """
        Parses an expression.

        Returns:
            Expr: The parsed expression.
        """
        return self._conditional()

    def _conditional(self) -> Expr:
        """
        Parses a conditional (ternary) expression.

        Returns:
            Expr: The parsed conditional expression.
        """
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
        """
        Parses an assignment expression.

        Returns:
            Expr: The parsed assignment expression.
        """
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
        """
        Parses logical OR expressions.

        Returns:
            Expr: The parsed logical OR expression.
        """
        expr: Expr = self._and()

        while self._match(TokenType.OR):
            operator: Token = self._previous()
            right: Expr = self._and()
            expr = Logical(expr, operator, right)

        return expr

    def _and(self) -> Expr:
        """
        Parses logical AND expressions.

        Returns:
            Expr: The parsed logical AND expression.
        """
        expr: Expr = self._equality()

        while self._match(TokenType.AND):
            operator: Token = self._previous()
            right: Expr = self._equality()
            expr = Logical(expr, operator, right)

        return expr

    def _equality(self) -> Expr:
        """
        Parses equality expressions.

        Returns:
            Expr: The parsed equality expression.
        """
        expr: Expr = self._comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self._previous()
            right: Expr = self._comparison()
            expr = Binary(expr, operator, right)

        return expr

    def _comparison(self) -> Expr:
        """
        Parses comparison expressions.

        Returns:
            Expr: The parsed comparison expression.
        """
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
        """
        Parses addition and subtraction expressions.

        Returns:
            Expr: The parsed term expression.
        """
        expr: Expr = self._factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self._previous()
            right: Expr = self._factor()
            expr = Binary(expr, operator, right)

        return expr

    def _factor(self) -> Expr:
        """
        Parses multiplication, division, and modulo expressions.

        Returns:
            Expr: The parsed factor expression.
        """
        expr: Expr = self._unary()

        while self._match(TokenType.SLASH, TokenType.STAR, TokenType.MODULO):
            operator: Token = self._previous()
            right: Expr = self._unary()
            expr = Binary(expr, operator, right)

        return expr

    def _unary(self) -> Expr:
        """
        Parses unary expressions.

        Returns:
            Expr: The parsed unary expression.
        """
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self._previous()
            right: Expr = self._unary()
            return Unary(operator, right)

        return self._call()

    def _call(self) -> Expr:
        """
        Parses function and method call expressions.

        Returns:
            Expr: The parsed call expression.
        """
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
        """
        Completes parsing of a function or method call.

        Args:
            callee (Expr): The expression being called.

        Returns:
            Expr: The parsed call expression.
        """
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
        """
        Parses primary expressions.

        Returns:
            Expr: The parsed primary expression.

        Raises:
            ParseError: If an unexpected token is encountered.
        """
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
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        raise self.error_handler.parse_error(
            token=self._peek(), message="Expect expression."
        )

    # Utility Methods

    def _advance(self) -> Token:
        """
        Advances to the next token.

        Returns:
            Token: The token that was advanced to.
        """
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _check(self, type: TokenType) -> bool:
        """
        Checks if the current token matches the given type.

        Args:
            type (TokenType): The token type to check against.

        Returns:
            bool: True if the current token matches the type, False otherwise.
        """
        return False if self._is_at_end() else self._peek().type == type

    def _match(self, *types: TokenType) -> bool:
        """
        Attempts to match the current token with any of the given types.

        Args:
            *types (TokenType): Variable length token types to match.

        Returns:
            bool: True if a match was found and the token was consumed, False otherwise.
        """
        for type in types:
            if self._check(type):
                self._advance()
                return True
        return False

    def _is_at_end(self) -> bool:
        """
        Checks if the parser has reached the end of the tokens.

        Returns:
            bool: True if at the end, False otherwise.
        """
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        """
        Returns the current token without consuming it.

        Returns:
            Token: The current token.
        """
        return self.tokens[self.current]

    def _previous(self) -> Token:
        """
        Returns the most recently consumed token.

        Returns:
            Token: The previous token.
        """
        return self.tokens[self.current - 1]

    def _consume(self, type: TokenType, message: str) -> Token:
        """
        Consumes the current token if it matches the expected type.

        Args:
            type (TokenType): The expected token type.
            message (str): The error message if the type does not match.

        Returns:
            Token: The consumed token.

        Raises:
            ParseError: If the current token does not match the expected type.
        """
        if self._check(type):
            return self._advance()
        raise self.error_handler.parse_error(token=self._peek(), message=message)

    def _synchronize(self) -> None:
        """
        Synchronizes the parser after encountering a parse error to continue parsing.
        """
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
