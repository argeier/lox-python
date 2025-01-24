import unittest
from typing import List
from unittest.mock import Mock

from lox.error_handler import ErrorHandler, ParseError
from lox.parser import Parser
from lox.stmt import Block, Expression, Function, If, Print, Return, Var, While
from lox.expr import Binary, Grouping, Literal, Variable
from lox.tokens import Token, TokenType


class TestParser(unittest.TestCase):
    def setUp(self):
        self.error_handler = Mock(spec=ErrorHandler)
        self.error_handler.parse_error.side_effect = ParseError

    def make_tokens(self, *token_types: TokenType, literals=None) -> List[Token]:
        if literals is None:
            literals = [None] * len(token_types)
        tokens = [
            Token(type, str(type), literal, 1)
            for type, literal in zip(token_types, literals)
        ]
        tokens.append(Token(TokenType.EOF, "", None, 1))
        return tokens

    def test_parse_number_literal(self):
        tokens = self.make_tokens(
            TokenType.NUMBER, TokenType.SEMICOLON, literals=[123.0, None]
        )
        parser = Parser(tokens, self.error_handler)
        statements = parser.parse()

        self.assertEqual(len(statements), 1)
        self.assertIsInstance(statements[0], Expression)
        self.assertIsInstance(statements[0].expression, Literal)
        self.assertEqual(statements[0].expression.value, 123.0)

    def test_parse_string_literal(self):
        tokens = self.make_tokens(
            TokenType.STRING, TokenType.SEMICOLON, literals=["test", None]
        )
        parser = Parser(tokens, self.error_handler)
        statements = parser.parse()

        self.assertEqual(len(statements), 1)
        self.assertIsInstance(statements[0], Expression)
        self.assertIsInstance(statements[0].expression, Literal)
        self.assertEqual(statements[0].expression.value, "test")

    def test_parse_grouping(self):
        tokens = self.make_tokens(
            TokenType.LEFT_PAREN,
            TokenType.NUMBER,
            TokenType.RIGHT_PAREN,
            TokenType.SEMICOLON,
            literals=[None, 123.0, None, None],
        )
        parser = Parser(tokens, self.error_handler)
        statements = parser.parse()

        self.assertEqual(len(statements), 1)
        self.assertIsInstance(statements[0], Expression)
        self.assertIsInstance(statements[0].expression, Grouping)
        self.assertIsInstance(statements[0].expression.expression, Literal)
        self.assertEqual(statements[0].expression.expression.value, 123.0)

    def test_parse_binary_expression(self):
        tokens = self.make_tokens(
            TokenType.NUMBER,
            TokenType.PLUS,
            TokenType.NUMBER,
            TokenType.SEMICOLON,
            literals=[1.0, None, 2.0, None],
        )
        parser = Parser(tokens, self.error_handler)
        statements = parser.parse()

        self.assertEqual(len(statements), 1)
        self.assertIsInstance(statements[0], Expression)
        expr = statements[0].expression
        self.assertIsInstance(expr, Binary)
        self.assertEqual(expr.operator.type, TokenType.PLUS)
        self.assertEqual(expr.left.value, 1.0)
        self.assertEqual(expr.right.value, 2.0)

    def test_parse_variable_declaration(self):
        tokens = self.make_tokens(
            TokenType.VAR,
            TokenType.IDENTIFIER,
            TokenType.EQUAL,
            TokenType.NUMBER,
            TokenType.SEMICOLON,
            literals=[None, "x", None, 123.0, None],
        )
        parser = Parser(tokens, self.error_handler)
        statements = parser.parse()

        self.assertEqual(len(statements), 1)
        self.assertIsInstance(statements[0], Var)
        self.assertEqual(statements[0].name.lexeme, "x")
        self.assertEqual(statements[0].initializer.value, 123.0)

    def test_parse_print_statement(self):
        tokens = self.make_tokens(
            TokenType.PRINT,
            TokenType.STRING,
            TokenType.SEMICOLON,
            literals=[None, "hello", None],
        )
        parser = Parser(tokens, self.error_handler)
        statements = parser.parse()

        self.assertEqual(len(statements), 1)
        self.assertIsInstance(statements[0], Print)
        self.assertEqual(statements[0].expression.value, "hello")

    def test_parse_block(self):
        tokens = self.make_tokens(
            TokenType.LEFT_BRACE,
            TokenType.VAR,
            TokenType.IDENTIFIER,
            TokenType.SEMICOLON,
            TokenType.RIGHT_BRACE,
            literals=[None, None, "x", None, None],
        )
        parser = Parser(tokens, self.error_handler)
        statements = parser.parse()

        self.assertEqual(len(statements), 1)
        self.assertIsInstance(statements[0], Block)
        self.assertEqual(len(statements[0].statements), 1)
        self.assertIsInstance(statements[0].statements[0], Var)

    def test_parse_if_statement(self):
        tokens = self.make_tokens(
            TokenType.IF,
            TokenType.LEFT_PAREN,
            TokenType.TRUE,
            TokenType.RIGHT_PAREN,
            TokenType.NUMBER,
            TokenType.SEMICOLON,
            literals=[None, None, None, None, 1.0, None],
        )
        parser = Parser(tokens, self.error_handler)
        statements = parser.parse()

        self.assertEqual(len(statements), 1)
        self.assertIsInstance(statements[0], If)
        self.assertEqual(statements[0].condition.value, True)

    def test_parse_while_statement(self):
        tokens = self.make_tokens(
            TokenType.WHILE,
            TokenType.LEFT_PAREN,
            TokenType.TRUE,
            TokenType.RIGHT_PAREN,
            TokenType.NUMBER,
            TokenType.SEMICOLON,
            literals=[None, None, None, None, 1.0, None],
        )
        parser = Parser(tokens, self.error_handler)
        statements = parser.parse()

        self.assertEqual(len(statements), 1)
        self.assertIsInstance(statements[0], While)
        self.assertEqual(statements[0].condition.value, True)

    def test_parse_function_declaration(self):
        tokens = self.make_tokens(
            TokenType.FUN,
            TokenType.IDENTIFIER,
            TokenType.LEFT_PAREN,
            TokenType.RIGHT_PAREN,
            TokenType.LEFT_BRACE,
            TokenType.RIGHT_BRACE,
            literals=[None, "test", None, None, None, None],
        )
        parser = Parser(tokens, self.error_handler)
        statements = parser.parse()

        self.assertEqual(len(statements), 1)
        self.assertIsInstance(statements[0], Function)
        self.assertEqual(statements[0].name.lexeme, "test")
        self.assertEqual(len(statements[0].params), 0)

    def test_parse_return_statement(self):
        tokens = self.make_tokens(
            TokenType.RETURN,
            TokenType.NUMBER,
            TokenType.SEMICOLON,
            literals=[None, 42.0, None],
        )
        parser = Parser(tokens, self.error_handler)
        statements = parser.parse()

        self.assertEqual(len(statements), 1)
        self.assertIsInstance(statements[0], Return)
        self.assertEqual(statements[0].value.value, 42.0)

    def test_parse_error_recovery(self):
        tokens = self.make_tokens(
            TokenType.VAR,
            TokenType.IDENTIFIER,  # Missing semicolon
            TokenType.PRINT,
            TokenType.STRING,
            TokenType.SEMICOLON,
            literals=[None, "x", None, "test", None],
        )
        parser = Parser(tokens, self.error_handler)
        statements = parser.parse()

        self.assertEqual(len(statements), 1)
        self.assertIsInstance(statements[0], Print)


if __name__ == "__main__":
    unittest.main()
