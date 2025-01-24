from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Final, Optional


class TokenType(Enum):
    """
    Enumeration of all possible token types in the Lox language.

    Categories:
        Single-character tokens: Tokens that consist of a single character.
        One or two character tokens: Tokens that may consist of one or two characters.
        Literals: Tokens representing literals like identifiers, strings, and numbers.
        Keywords: Reserved words in the Lox language.
        EOF: Represents the end of the file/input.
    """

    # Single-character tokens
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    COMMA = ","
    DOT = "."
    MINUS = "-"
    PLUS = "+"
    SEMICOLON = ";"
    SLASH = "/"
    STAR = "*"
    QUESTION = "?"
    COLON = ":"
    MODULO = "%"

    # One or two character tokens
    BANG = "!"
    BANG_EQUAL = "!="
    EQUAL = "="
    EQUAL_EQUAL = "=="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="

    # Literals
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"

    # Keywords
    AND = "and"
    CLASS = "class"
    ELSE = "else"
    FALSE = "false"
    FUN = "fun"
    FOR = "for"
    IF = "if"
    NIL = "nil"
    OR = "or"
    PRINT = "print"
    RETURN = "return"
    SUPER = "super"
    THIS = "this"
    TRUE = "true"
    VAR = "var"
    WHILE = "while"
    FUNCTION = "function"
    BREAK = "break"
    TRAIT = "trait"
    WITH = "with"

    # End of file
    EOF = "EOF"


class Token:
    """
    Represents a token produced by the scanner.

    Attributes:
        type (TokenType): The type of the token.
        lexeme (str): The lexeme (actual text) of the token.
        literal (Optional[Any]): The literal value of the token, if any.
        line (int): The line number where the token appears.
    """

    __slots__ = ("type", "lexeme", "literal", "line")

    def __init__(
        self, type: TokenType, lexeme: str, literal: Optional[Any], line: int
    ) -> None:
        self.type: TokenType = type
        self.lexeme: str = lexeme
        self.literal: Optional[Any] = literal
        self.line: int = line

    def __str__(self) -> str:
        return f"{self.type} {self.lexeme} {self.literal}"


# Define the set of reserved keyword values
KEYWORD_VALUES: Final[set[str]] = {
    "and",
    "class",
    "else",
    "false",
    "fun",
    "for",
    "if",
    "nil",
    "or",
    "print",
    "return",
    "super",
    "this",
    "true",
    "var",
    "while",
    "break",
    "trait",
    "with",
}

# Create a dictionary mapping keyword strings to their TokenType
KEYWORDS: Final[Dict[str, TokenType]] = {
    token_type.value: token_type
    for token_type in TokenType
    if token_type.value in KEYWORD_VALUES
}
