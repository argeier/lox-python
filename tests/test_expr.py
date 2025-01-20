import unittest
from unittest.mock import Mock, patch

from src.lox.expr import (
    Assign,
    Binary,
    Call,
    ExprVisitor,
    Grouping,
    Literal,
    Logical,
    Unary,
    Variable,
)
from src.lox.tokens import Token, TokenType  # Update this import too


class TestExprVisitor(ExprVisitor[None]):
    def visit_binary_expr(self, expr: Binary) -> None:
        pass

    def visit_call_expr(self, expr: Call) -> None:
        pass

    def visit_grouping_expr(self, expr: Grouping) -> None:
        pass

    def visit_literal_expr(self, expr: Literal) -> None:
        pass

    def visit_unary_expr(self, expr: Unary) -> None:
        pass

    def visit_variable_expr(self, expr: Variable) -> None:
        pass

    def visit_assign_expr(self, expr: Assign) -> None:
        pass

    def visit_logical_expr(self, expr: Logical) -> None:
        pass


class TestExpr(unittest.TestCase):
    def setUp(self):
        self.visitor = Mock(spec=TestExprVisitor)

    def test_binary_expr(self):
        left = Literal(1)
        operator = Token(TokenType.PLUS, "+", None, 1)
        right = Literal(2)
        expr = Binary(left, operator, right)
        expr.accept(self.visitor)
        self.visitor.visit_binary_expr.assert_called_once_with(expr)

    def test_call_expr(self):
        callee = Literal("callee")
        paren = Token(TokenType.LEFT_PAREN, "(", None, 1)
        arguments = [Literal(1)]
        expr = Call(callee, paren, arguments)
        expr.accept(self.visitor)
        self.visitor.visit_call_expr.assert_called_once_with(expr)

    def test_grouping_expr(self):
        expression = Literal(1)
        expr = Grouping(expression)
        expr.accept(self.visitor)
        self.visitor.visit_grouping_expr.assert_called_once_with(expr)

    def test_literal_expr(self):
        expr = Literal(1)
        expr.accept(self.visitor)
        self.visitor.visit_literal_expr.assert_called_once_with(expr)

    def test_unary_expr(self):
        operator = Token(TokenType.MINUS, "-", None, 1)
        right = Literal(1)
        expr = Unary(operator, right)
        expr.accept(self.visitor)
        self.visitor.visit_unary_expr.assert_called_once_with(expr)

    def test_variable_expr(self):
        name = Token(TokenType.IDENTIFIER, "x", None, 1)
        expr = Variable(name)
        expr.accept(self.visitor)
        self.visitor.visit_variable_expr.assert_called_once_with(expr)

    def test_assign_expr(self):
        name = Token(TokenType.IDENTIFIER, "x", None, 1)
        value = Literal(1)
        expr = Assign(name, value)
        expr.accept(self.visitor)
        self.visitor.visit_assign_expr.assert_called_once_with(expr)

    def test_logical_expr(self):
        left = Literal(True)
        operator = Token(TokenType.OR, "or", None, 1)
        right = Literal(False)
        expr = Logical(left, operator, right)
        expr.accept(self.visitor)
        self.visitor.visit_logical_expr.assert_called_once_with(expr)


if __name__ == "__main__":
    unittest.main()
