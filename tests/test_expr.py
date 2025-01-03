import os
import sys
import unittest
from typing import Any

# Append the source directory to the system path
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")

from expr import Binary, ExprVisitor, Grouping, Literal, Unary
from tokens import Token, TokenType


class MockVisitor(ExprVisitor[str]):
    def visit_binary_expr(self, expr: Binary) -> str:
        return "Binary"

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return "Grouping"

    def visit_literal_expr(self, expr: Literal) -> str:
        return f"Literal({expr.value})"

    def visit_unary_expr(self, expr: Unary) -> str:
        return "Unary"


class TestExpr(unittest.TestCase):

    def setUp(self) -> None:
        self.visitor: MockVisitor = MockVisitor()

    def test_literal_expr(self) -> None:
        literal: Literal = Literal(42)
        result: str = literal.accept(self.visitor)
        self.assertEqual(result, "Literal(42)")

    def test_binary_expr(self) -> None:
        left: Literal = Literal(1)
        operator: Token = Token(TokenType.PLUS, "+", None, 1)
        right: Literal = Literal(2)
        binary: Binary = Binary(left, operator, right)
        result: str = binary.accept(self.visitor)
        self.assertEqual(result, "Binary")

    def test_grouping_expr(self) -> None:
        expression: Literal = Literal(3)
        grouping: Grouping = Grouping(expression)
        result: str = grouping.accept(self.visitor)
        self.assertEqual(result, "Grouping")

    def test_unary_expr(self) -> None:
        operator: Token = Token(TokenType.MINUS, "-", None, 1)
        right: Literal = Literal(4)
        unary: Unary = Unary(operator, right)
        result: str = unary.accept(self.visitor)
        self.assertEqual(result, "Unary")


if __name__ == "__main__":
    unittest.main()
