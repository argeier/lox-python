from enum import Enum
from typing import Any, Dict, Final, Optional


class TokenType(Enum):
    """
    Represents all possible token types in the language.

    Attributes:
        - Single-character tokens: Characters that represent specific operators or syntax.
        - One or two character tokens: Symbols that may represent different meanings based on the following character.
        - Literals: Identifiers, strings, and numbers in the language.
        - Keywords: Reserved words in the language.
        - EOF: End-of-file token to signify the end of the source.
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

    # End of file
    EOF = "EOF"


class Token:
    """
    Represents a single token in the source code.

    Attributes:
        type (TokenType): The type of the token.
        lexeme (str): The actual string representation of the token.
        literal (Optional[Any]): The literal value associated with the token, if any.
        line (int): The line number where the token occurs.
    """

    def __init__(self, type: TokenType, lexeme: str, literal: Optional[Any], line: int):
        """
        Initializes a Token instance.

        Args:
            type (TokenType): The type of the token.
            lexeme (str): The string representation of the token.
            literal (Optional[Any]): The literal value of the token, if applicable.
            line (int): The line number where the token is located.
        """
        self.type: TokenType = type
        self.lexeme: str = lexeme
        self.literal: Optional[Any] = literal
        self.line: int = line

    def __str__(self) -> str:
        """
        Returns a string representation of the token.

        Returns:
            str: The formatted string representation of the token.
        """
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
}

# Create a dictionary mapping keyword strings to their TokenType
KEYWORDS: Final[Dict[str, TokenType]] = {
    token_type.value: token_type
    for token_type in TokenType
    if token_type.value in KEYWORD_VALUES
}
