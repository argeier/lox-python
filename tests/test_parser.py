import os
import sys
import unittest
from unittest.mock import Mock

# Append the source directory to the system path
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")

from error_handler import ErrorHandler
from scanner import Scanner
from tokens import Token, TokenType


class TestScanner(unittest.TestCase):
    def setUp(self):
        self.error_handler = Mock(spec=ErrorHandler)

    def test_single_character_tokens(self):
        source = "(){}.,-+;*"
        scanner = Scanner(source, self.error_handler)
        tokens = scanner.scan_tokens()

        expected_types = [
            TokenType.LEFT_PAREN,
            TokenType.RIGHT_PAREN,
            TokenType.LEFT_BRACE,
            TokenType.RIGHT_BRACE,
            TokenType.DOT,
            TokenType.COMMA,
            TokenType.MINUS,
            TokenType.PLUS,
            TokenType.SEMICOLON,
            TokenType.STAR,
            TokenType.EOF,
        ]

        self.assertEqual(len(tokens), len(expected_types))
        for token, expected_type in zip(tokens, expected_types):
            self.assertEqual(token.type, expected_type)

    def test_two_character_tokens(self):
        source = "!= == <= >= // /* */"
        scanner = Scanner(source, self.error_handler)
        tokens = scanner.scan_tokens()

        expected_types = [
            TokenType.BANG_EQUAL,
            TokenType.EQUAL_EQUAL,
            TokenType.LESS_EQUAL,
            TokenType.GREATER_EQUAL,
            TokenType.EOF,
        ]

        self.assertEqual(len(tokens), len(expected_types))
        for token, expected_type in zip(tokens, expected_types):
            self.assertEqual(token.type, expected_type)

    def test_string_token(self):
        source = '"hello world"'
        scanner = Scanner(source, self.error_handler)
        tokens = scanner.scan_tokens()

        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].literal, "hello world")
        self.assertEqual(tokens[1].type, TokenType.EOF)

    def test_number_token(self):
        source = "123 45.67"
        scanner = Scanner(source, self.error_handler)
        tokens = scanner.scan_tokens()

        self.assertEqual(len(tokens), 3)
        self.assertEqual(tokens[0].type, TokenType.NUMBER)
        self.assertEqual(tokens[0].literal, 123)
        self.assertEqual(tokens[1].type, TokenType.NUMBER)
        self.assertEqual(tokens[1].literal, 45.67)
        self.assertEqual(tokens[2].type, TokenType.EOF)

    def test_identifier_token(self):
        source = "varName"
        scanner = Scanner(source, self.error_handler)
        tokens = scanner.scan_tokens()

        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].lexeme, "varName")
        self.assertEqual(tokens[1].type, TokenType.EOF)

    def test_keyword_token(self):
        source = "if else while for"
        scanner = Scanner(source, self.error_handler)
        tokens = scanner.scan_tokens()

        expected_types = [
            TokenType.IF,
            TokenType.ELSE,
            TokenType.WHILE,
            TokenType.FOR,
            TokenType.EOF,
        ]

        self.assertEqual(len(tokens), len(expected_types))
        for token, expected_type in zip(tokens, expected_types):
            self.assertEqual(token.type, expected_type)

    def test_unterminated_string(self):
        source = '"hello world'
        scanner = Scanner(source, self.error_handler)
        tokens = scanner.scan_tokens()

        self.error_handler.error.assert_called_once_with(
            line=1, message="Unterminated string."
        )

    def test_unterminated_block_comment(self):
        source = "/* comment"
        scanner = Scanner(source, self.error_handler)
        tokens = scanner.scan_tokens()

        self.error_handler.error.assert_called_once_with(
            line=1, message="Unterminated block comment."
        )


if __name__ == "__main__":
    unittest.main()
