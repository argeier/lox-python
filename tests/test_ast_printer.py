import os
import sys
import unittest
from typing import Any

# Append the source directory to the system path
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")

from ast_printer import AstPrinter
from expr import Binary, Grouping, Literal, Unary, Visitor
from tokens import Token, TokenType


class MockVisitor(Visitor[str]):
    """
    Mock implementation of Visitor for testing purposes.
    Each method returns a simple string representation of the expression type.
    """

    def visit_binary_expr(self, expr: Binary) -> str:
        """
        Visit a Binary expression.

        Args:
            expr (Binary): The binary expression to visit.

        Returns:
            str: String representation of the binary expression.
        """
        return "Binary"

    def visit_grouping_expr(self, expr: Grouping) -> str:
        """
        Visit a Grouping expression.

        Args:
            expr (Grouping): The grouping expression to visit.

        Returns:
            str: String representation of the grouping expression.
        """
        return "Grouping"

    def visit_literal_expr(self, expr: Literal) -> str:
        """
        Visit a Literal expression.

        Args:
            expr (Literal): The literal expression to visit.

        Returns:
            str: String representation of the literal expression.
        """
        return f"Literal({expr.value})"

    def visit_unary_expr(self, expr: Unary) -> str:
        """
        Visit a Unary expression.

        Args:
            expr (Unary): The unary expression to visit.

        Returns:
            str: String representation of the unary expression.
        """
        return "Unary"


class TestAstPrinter(unittest.TestCase):
    """
    Unit tests for the AstPrinter class and Visitor pattern implementation.
    Ensures that AST generation and visitor methods produce the expected output.
    """

    def setUp(self) -> None:
        """
        Set up the test environment.

        Initializes an instance of AstPrinter and MockVisitor for use in test cases.
        """
        self.printer: AstPrinter = AstPrinter()
        self.visitor: MockVisitor = MockVisitor()

    def test_literal_expression(self) -> None:
        """
        Test the AST generation for a literal expression.

        Ensures that the literal expression is printed and visited correctly.
        """
        literal: Literal = Literal(123)
        self.printer.create_ast(literal)
        self.assertEqual(self.printer.ast, "123")

        # Test Visitor pattern
        result: str = literal.accept(self.visitor)
        self.assertEqual(result, "Literal(123)")

    def test_grouping_expression(self) -> None:
        """
        Test the AST generation for a grouping expression.

        Ensures that the grouping expression is printed and visited correctly.
        """
        expression: Grouping = Grouping(Literal(45.67))
        self.printer.create_ast(expression)
        self.assertEqual(self.printer.ast, "(group 45.67)")

        # Test Visitor pattern
        result: str = expression.accept(self.visitor)
        self.assertEqual(result, "Grouping")

    def test_unary_expression(self) -> None:
        """
        Test the AST generation for a unary expression.

        Ensures that the unary expression is printed and visited correctly.
        """
        unary: Unary = Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123))
        self.printer.create_ast(unary)
        self.assertEqual(self.printer.ast, "(- 123)")

        # Test Visitor pattern
        result: str = unary.accept(self.visitor)
        self.assertEqual(result, "Unary")

    def test_binary_expression(self) -> None:
        """
        Test the AST generation for a binary expression.

        Ensures that the binary expression is printed and visited correctly.
        """
        binary: Binary = Binary(
            Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
            Token(TokenType.STAR, "*", None, 1),
            Grouping(Literal(45.67)),
        )
        self.printer.create_ast(binary)
        self.assertEqual(self.printer.ast, "(* (- 123) (group 45.67))")

        # Test Visitor pattern
        result: str = binary.accept(self.visitor)
        self.assertEqual(result, "Binary")


if __name__ == "__main__":
    unittest.main()
