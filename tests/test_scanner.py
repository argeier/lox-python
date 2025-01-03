import os
import sys
import unittest
from typing import List

# Append the source directory to the system path
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")

from error_handler import ErrorHandler
from scanner import Scanner
from tokens import KEYWORDS, Token, TokenType


class TestScanner(unittest.TestCase):

    def setUp(self) -> None:
        self.error_handler: ErrorHandler = ErrorHandler()

    def test_scan_tokens(self) -> None:
        lox_code = """/* This is a comment
        /* Nested comment */
        Still inside the outer comment */

        class HelloWorld {
          fun sayHello() {
            print "Hello, World!";
          }
        }

        var counter = 0;

        while (counter < 10) {
          print counter;
          counter = counter + 1;
        }

        if (counter == 10) {
          print "Counter reached 10.";
        } else {
          print "POOP.";
        }
        """

        scanner = Scanner(lox_code, self.error_handler)
        tokens: List[Token] = scanner.scan_tokens()

        expected_tokens = [
            TokenType.CLASS,
            TokenType.IDENTIFIER,  # HelloWorld
            TokenType.LEFT_BRACE,
            TokenType.FUN,
            TokenType.IDENTIFIER,  # sayHello
            TokenType.LEFT_PAREN,
            TokenType.RIGHT_PAREN,
            TokenType.LEFT_BRACE,
            TokenType.PRINT,
            TokenType.STRING,  # "Hello, World!"
            TokenType.SEMICOLON,
            TokenType.RIGHT_BRACE,
            TokenType.RIGHT_BRACE,
            TokenType.VAR,
            TokenType.IDENTIFIER,  # counter
            TokenType.EQUAL,
            TokenType.NUMBER,  # 0
            TokenType.SEMICOLON,
            TokenType.WHILE,
            TokenType.LEFT_PAREN,
            TokenType.IDENTIFIER,  # counter
            TokenType.LESS,
            TokenType.NUMBER,  # 10
            TokenType.RIGHT_PAREN,
            TokenType.LEFT_BRACE,
            TokenType.PRINT,
            TokenType.IDENTIFIER,  # counter
            TokenType.SEMICOLON,
            TokenType.IDENTIFIER,  # counter
            TokenType.EQUAL,
            TokenType.IDENTIFIER,  # counter
            TokenType.PLUS,
            TokenType.NUMBER,  # 1
            TokenType.SEMICOLON,
            TokenType.RIGHT_BRACE,
            TokenType.IF,
            TokenType.LEFT_PAREN,
            TokenType.IDENTIFIER,  # counter
            TokenType.EQUAL_EQUAL,
            TokenType.NUMBER,  # 10
            TokenType.RIGHT_PAREN,
            TokenType.LEFT_BRACE,
            TokenType.PRINT,
            TokenType.STRING,  # "Counter reached 10."
            TokenType.SEMICOLON,
            TokenType.RIGHT_BRACE,
            TokenType.ELSE,
            TokenType.LEFT_BRACE,
            TokenType.PRINT,
            TokenType.STRING,  # "POOP."
            TokenType.SEMICOLON,
            TokenType.RIGHT_BRACE,
            TokenType.EOF,
        ]

        actual_types = [token.type for token in tokens]
        expected_types = expected_tokens

        self.assertEqual(actual_types, expected_types)

    def test_comment_handling(self) -> None:
        lox_code = """
        /* Outer comment
           /* Nested comment */
           Still part of the comment */
        var x = 5; // Single-line comment
        """

        scanner = Scanner(lox_code, self.error_handler)
        tokens: List[Token] = scanner.scan_tokens()

        expected_tokens = [
            TokenType.VAR,
            TokenType.IDENTIFIER,  # x
            TokenType.EQUAL,
            TokenType.NUMBER,  # 5
            TokenType.SEMICOLON,
            TokenType.EOF,
        ]

        actual_types = [token.type for token in tokens]
        expected_types = expected_tokens

        self.assertEqual(actual_types, expected_types)

    def test_error_handling(self) -> None:
        lox_code = """
        "Unterminated string
        """

        scanner = Scanner(lox_code, self.error_handler)
        tokens: List[Token] = scanner.scan_tokens()

        # Expect an error for unterminated string
        self.assertTrue(self.error_handler.had_error)
        self.assertIn("Unterminated string", "\n".join(self.error_handler.errors))

    def test_nested_comments(self) -> None:
        lox_code = """
        /* Comment
           /* Nested */
           Still part of outer */
        var y = 10;
        """

        scanner = Scanner(lox_code, self.error_handler)
        tokens: List[Token] = scanner.scan_tokens()

        expected_tokens = [
            TokenType.VAR,
            TokenType.IDENTIFIER,  # y
            TokenType.EQUAL,
            TokenType.NUMBER,  # 10
            TokenType.SEMICOLON,
            TokenType.EOF,
        ]

        actual_types = [token.type for token in tokens]
        expected_types = expected_tokens

        self.assertEqual(actual_types, expected_types)


if __name__ == "__main__":
    unittest.main()
