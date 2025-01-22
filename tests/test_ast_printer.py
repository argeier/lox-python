"""Tests for the AST Printer module."""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from lox.ast_printer import AstPrinter
from lox.expr import Binary, Grouping, Literal, Unary, Variable
from lox.stmt import Block, Break, Expression, If, Return, While
from lox.tokens import Token, TokenType


class TestAstPrinter(unittest.TestCase):
    def setUp(self):
        """Set up fresh AST printer instance for each test."""
        self.ast_printer = AstPrinter()
        self.ast_printer._output_dir = Path("test_output")

    def tearDown(self):
        """Clean up any test artifacts."""
        if self.ast_printer._output_dir.exists():
            import shutil

            shutil.rmtree(self.ast_printer._output_dir)

    def test_initialization(self):
        """Test proper initialization of AstPrinter."""
        self.assertEqual(self.ast_printer._ast, "")
        self.assertEqual(self.ast_printer._visited_nodes, set())
        self.assertFalse(self.ast_printer._ast_directory_cleared)
        self.assertEqual(self.ast_printer._node_counter, 0)

    def test_create_ast_none(self):
        """Test creating AST with None statement."""
        self.ast_printer.create_ast(None)
        self.assertEqual(self.ast_printer.ast, "")

    def test_split_expression(self):
        """Test expression splitting functionality."""
        test_cases = [
            ("(+ 1 2)", ["(+ 1 2)"]),
            ('(print "hello")', ['(print "hello")']),
            ("(+ (* 3 4) 5)", ["(+ (* 3 4) 5)"]),
            ('"test string"', ['"test string"']),
        ]
        for input_expr, expected in test_cases:
            with self.subTest(input_expr=input_expr):
                result = self.ast_printer._split_expression(input_expr)
                self.assertEqual(result, expected)

    def test_visit_literal_expr(self):
        """Test literal expression visiting."""
        test_cases = [
            (None, "nil"),
            ("hello", '"hello"'),
            (42, "42"),
            (3.14, "3.14"),
            (True, "True"),
        ]
        for value, expected in test_cases:
            with self.subTest(value=value):
                expr = Literal(value)
                result = self.ast_printer.visit_literal_expr(expr)
                self.assertEqual(result, expected)

    def test_visit_binary_expr(self):
        """Test binary expression visiting."""
        left = Literal(1)
        right = Literal(2)
        operator = Token(TokenType.PLUS, "+", None, 1)
        expr = Binary(left, operator, right)
        result = self.ast_printer.visit_binary_expr(expr)
        self.assertEqual(result, "(+ 1 2)")

    def test_visit_grouping_expr(self):
        """Test grouping expression visiting."""
        inner = Literal(42)
        expr = Grouping(inner)
        result = self.ast_printer.visit_grouping_expr(expr)
        self.assertEqual(result, "(group 42)")

    def test_visit_unary_expr(self):
        """Test unary expression visiting."""
        operator = Token(TokenType.MINUS, "-", None, 1)
        right = Literal(5)
        expr = Unary(operator, right)
        result = self.ast_printer.visit_unary_expr(expr)
        self.assertEqual(result, "(- 5)")

    def test_visit_variable_expr(self):
        """Test variable expression visiting."""
        name = Token(TokenType.IDENTIFIER, "x", None, 1)
        expr = Variable(name)
        result = self.ast_printer.visit_variable_expr(expr)
        self.assertEqual(result, "x")

    def test_visit_block_stmt(self):
        """Test block statement visiting."""
        statements = [Expression(Literal(1)), Expression(Literal(2))]
        stmt = Block(statements)
        result = self.ast_printer.visit_block_stmt(stmt)
        self.assertEqual(result, "(block (expr 1) (expr 2))")

    def test_visit_if_stmt(self):
        """Test if statement visiting with and without else branch."""
        condition = Literal(True)
        then_branch = Expression(Literal(1))

        # Test if without else
        stmt = If(condition, then_branch, None)
        result = self.ast_printer.visit_if_stmt(stmt)
        self.assertEqual(result, "(if True (expr 1))")

        # Test if with else
        else_branch = Expression(Literal(2))
        stmt = If(condition, then_branch, else_branch)
        result = self.ast_printer.visit_if_stmt(stmt)
        self.assertEqual(result, "(if True (expr 1) (expr 2))")

    def test_visualize_ast(self):
        """Test AST visualization."""
        # Prepare the test
        self.ast_printer._ast = "(+ 1 2)"

        with patch("lox.ast_printer.AGraph") as MockAGraph, patch(
            "builtins.print"
        ) as mock_print:  # Prevent print output
            # Setup the mock
            mock_graph = MagicMock()
            MockAGraph.return_value = mock_graph
            mock_graph.draw.return_value = None  # Prevent actual file writing

            # Execute the method
            self.ast_printer.visualize_ast()

            # Verify the mock was called correctly
            MockAGraph.assert_called_once_with(strict=True, directed=True)
            mock_graph.layout.assert_called_once_with(prog="dot")
            mock_graph.draw.assert_called_once()

            # Verify no actual file operations occurred
            self.assertFalse(Path("test_output/ast_statement_0.png").exists())

    def test_break_stmt(self):
        """Test break statement visiting."""
        stmt = Break()
        result = self.ast_printer.visit_break_stmt(stmt)
        self.assertEqual(result, "(break)")

    def test_return_stmt(self):
        """Test return statement visiting with and without value."""
        # Test return without value
        stmt = Return(Token(TokenType.RETURN, "return", None, 1), None)
        result = self.ast_printer.visit_return_stmt(stmt)
        self.assertEqual(result, "(return)")

        # Test return with value
        stmt = Return(Token(TokenType.RETURN, "return", None, 1), Literal(42))
        result = self.ast_printer.visit_return_stmt(stmt)
        self.assertEqual(result, "(return 42)")

    def test_while_stmt(self):
        """Test while statement visiting."""
        condition = Literal(True)
        body = Expression(Literal(42))
        stmt = While(condition, body)
        result = self.ast_printer.visit_while_stmt(stmt)
        self.assertEqual(result, "(while True (expr 42))")


if __name__ == "__main__":
    unittest.main()
