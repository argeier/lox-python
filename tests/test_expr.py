import os
import sys
import unittest
from typing import Any

# Append the source directory to the system path
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")

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


class TestExpr(unittest.TestCase):
    """
    Unit tests for expressions and the Visitor pattern implementation.
    Ensures that visitor methods produce the expected output for each expression type.
    """

    def setUp(self) -> None:
        """
        Set up the test environment.

        Initializes an instance of MockVisitor for use in test cases.
        """
        self.visitor: MockVisitor = MockVisitor()

    def test_literal_expr(self) -> None:
        """
        Test the visitor pattern for a literal expression.

        Ensures that the Literal expression is visited correctly.
        """
        literal: Literal = Literal(42)
        result: str = literal.accept(self.visitor)
        self.assertEqual(result, "Literal(42)")

    def test_binary_expr(self) -> None:
        """
        Test the visitor pattern for a binary expression.

        Ensures that the Binary expression is visited correctly.
        """
        left: Literal = Literal(1)
        operator: Token = Token(TokenType.PLUS, "+", None, 1)
        right: Literal = Literal(2)
        binary: Binary = Binary(left, operator, right)
        result: str = binary.accept(self.visitor)
        self.assertEqual(result, "Binary")

    def test_grouping_expr(self) -> None:
        """
        Test the visitor pattern for a grouping expression.

        Ensures that the Grouping expression is visited correctly.
        """
        expression: Literal = Literal(3)
        grouping: Grouping = Grouping(expression)
        result: str = grouping.accept(self.visitor)
        self.assertEqual(result, "Grouping")

    def test_unary_expr(self) -> None:
        """
        Test the visitor pattern for a unary expression.

        Ensures that the Unary expression is visited correctly.
        """
        operator: Token = Token(TokenType.MINUS, "-", None, 1)
        right: Literal = Literal(4)
        unary: Unary = Unary(operator, right)
        result: str = unary.accept(self.visitor)
        self.assertEqual(result, "Unary")


if __name__ == "__main__":
    unittest.main()
