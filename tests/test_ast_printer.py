import os
import sys
import unittest
from typing import Any

# Append the source directory to the system path
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")

from ast_printer import AstPrinter
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


class TestAstPrinter(unittest.TestCase):

    def setUp(self) -> None:
        self.printer: AstPrinter = AstPrinter()
        self.visitor: MockVisitor = MockVisitor()

    def test_literal_expression(self) -> None:
        literal: Literal = Literal(123)
        self.printer.create_ast(literal)
        self.assertEqual(self.printer.ast, "123")

        # Test ExprVisitor pattern
        result: str = literal.accept(self.visitor)
        self.assertEqual(result, "Literal(123)")

    def test_grouping_expression(self) -> None:
        expression: Grouping = Grouping(Literal(45.67))
        self.printer.create_ast(expression)
        self.assertEqual(self.printer.ast, "(group 45.67)")

        # Test ExprVisitor pattern
        result: str = expression.accept(self.visitor)
        self.assertEqual(result, "Grouping")

    def test_unary_expression(self) -> None:
        unary: Unary = Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123))
        self.printer.create_ast(unary)
        self.assertEqual(self.printer.ast, "(- 123)")

        # Test ExprVisitor pattern
        result: str = unary.accept(self.visitor)
        self.assertEqual(result, "Unary")

    def test_binary_expression(self) -> None:
        binary: Binary = Binary(
            Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
            Token(TokenType.STAR, "*", None, 1),
            Grouping(Literal(45.67)),
        )
        self.printer.create_ast(binary)
        self.assertEqual(self.printer.ast, "(* (- 123) (group 45.67))")

        # Test ExprVisitor pattern
        result: str = binary.accept(self.visitor)
        self.assertEqual(result, "Binary")


if __name__ == "__main__":
    unittest.main()
