from typing import List, Optional

from error_handler import ErrorHandler
from tokens import KEYWORDS, Token, TokenType


class Scanner:
    """
    A lexical analyzer (scanner) for breaking a source string into tokens.

    Attributes:
        source (str): The input source code as a string.
        error_handler (ErrorHandler): Handler for reporting errors.
        tokens (List[Token]): List to store generated tokens.
        start (int): Start index of the current lexeme.
        current (int): Current index in the source code.
        line (int): Current line number in the source code.
        line_current (int): Current position within the line.
    """

    def __init__(self, source: str, error_handler: ErrorHandler):
        """
        Initializes the scanner with source code and an error handler.

        Args:
            source (str): The source code to scan.
            error_handler (ErrorHandler): The error handler instance.
        """
        self.source: str = source
        self.error_handler: ErrorHandler = error_handler
        self.tokens: List[Token] = []
        self.start: int = 0
        self.current: int = 0
        self.line: int = 1
        self.line_current: int = 0  # Current position at self.line

    def scan_tokens(self) -> List[Token]:
        """
        Scans the source code and generates a list of tokens.

        Returns:
            List[Token]: The list of tokens generated from the source code.
        """
        while not self._is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(
            Token(type=TokenType.EOF, lexeme="", literal=None, line=self.line)
        )
        return self.tokens

    def _is_at_end(self) -> bool:
        """
        Checks if the scanner has reached the end of the source code.

        Returns:
            bool: True if at the end, otherwise False.
        """
        return self.current >= len(self.source)

    def _advance(self) -> str:
        """
        Advances the scanner by one character.

        Returns:
            str: The character at the current position before advancing.
        """
        self.current += 1
        self.line_current += 1
        return self.source[self.current - 1]

    def _advance_two(self) -> None:
        """
        Advances the scanner by two characters.
        """
        for _ in range(2):
            self._advance()

    def _peek(self) -> str:
        """
        Peeks at the current character without advancing.

        Returns:
            str: The current character, or '\0' if at the end.
        """
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self) -> str:
        """
        Peeks at the next character without advancing.

        Returns:
            str: The next character, or '\0' if at the end.
        """
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def _match(self, expected: str) -> bool:
        """
        Matches the current character with an expected character.

        Args:
            expected (str): The character to match.

        Returns:
            bool: True if matched, otherwise False.
        """
        if self._is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        self.line_current += 1
        return True

    def add_token(self, type: TokenType, literal: Optional[object] = None) -> None:
        """
        Adds a token to the token list.

        Args:
            type (TokenType): The type of the token.
            literal (Optional[object]): The literal value of the token.
        """
        text = self.source[self.start : self.current]
        self.tokens.append(
            Token(type=type, lexeme=text, literal=literal, line=self.line)
        )

    def _update_line(self) -> None:
        """
        Updates the line and resets the line position.
        """
        self.line += 1
        self.line_current = 0

    def scan_token(self) -> None:
        """
        Scans the current lexeme and identifies the token type.
        """
        c: str = self._advance()
        match c:
            case "(":
                self.add_token(TokenType.LEFT_PAREN)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN)
            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE)
            case ",":
                self.add_token(TokenType.COMMA)
            case ".":
                self.add_token(TokenType.DOT)
            case "-":
                self.add_token(TokenType.MINUS)
            case "+":
                self.add_token(TokenType.PLUS)
            case ";":
                self.add_token(TokenType.SEMICOLON)
            case "*":
                self.add_token(TokenType.STAR)
            case "!":
                self.add_token(
                    TokenType.BANG_EQUAL if self._match("=") else TokenType.BANG
                )
            case "=":
                self.add_token(
                    TokenType.EQUAL_EQUAL if self._match("=") else TokenType.EQUAL
                )
            case "<":
                self.add_token(
                    TokenType.LESS_EQUAL if self._match("=") else TokenType.LESS
                )
            case ">":
                self.add_token(
                    TokenType.GREATER_EQUAL if self._match("=") else TokenType.GREATER
                )
            case "/":
                if self._match("/"):
                    while self._peek() != "\n" and not self._is_at_end():
                        self._advance()
                elif self._match("*"):
                    self.block_comment()
                else:
                    self.add_token(TokenType.SLASH)
            case " " | "\r" | "\t":
                pass
            case "\n":
                self._update_line()
            case '"':
                self.string()
            case _:
                if c.isdigit():
                    self.number()
                elif c.isalnum():
                    self.identifier()
                else:
                    self.error_handler.error(
                        line=self.line,
                        message=f"Token {c} at position {self.line_current} not accepted",
                    )

    def string(self) -> None:
        """
        Processes string literals.
        """
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == "\n":
                self._update_line()
            self._advance()
        if self._is_at_end():
            self.error_handler.error(line=self.line, message="Unterminated string.")
            return
        self._advance()
        value: str = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number(self) -> None:
        """
        Processes numeric literals.
        """
        while self._peek().isdigit():
            self._advance()
        if self._peek() == "." and self._peek_next().isdigit():
            self._advance()
            while self._peek().isdigit():
                self._advance()
        self.add_token(TokenType.NUMBER, float(self.source[self.start : self.current]))

    def identifier(self) -> None:
        """
        Processes identifiers and reserved keywords.
        """
        while self._peek().isalnum():
            self._advance()
        text: str = self.source[self.start : self.current]
        token_type: TokenType = KEYWORDS.get(text, TokenType.IDENTIFIER)
        self.add_token(token_type)

    def block_comment(self) -> None:
        """
        Processes block comments, including nested comments.
        """
        nesting_level: int = 1
        while not self._is_at_end():
            if self._peek() == "/" and self._peek_next() == "*":
                self._advance_two()
                nesting_level += 1
            elif self._peek() == "*" and self._peek_next() == "/":
                self._advance_two()
                nesting_level -= 1
                if nesting_level == 0:
                    return
            if self._peek() == "\n":
                self._update_line()
            self._advance()
        self.error_handler.error(line=self.line, message="Unterminated block comment.")
