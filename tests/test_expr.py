import unittest
from unittest.mock import Mock

from lox.expr import (
    Assign,
    Binary,
    Call,
    Conditional,
    Expr,
    ExprVisitor,
    Get,
    Grouping,
    Literal,
    Logical,
    Set,
    Super,
    This,
    Unary,
    Variable,
)
from lox.tokens import Token, TokenType


class TestExprVisitor(ExprVisitor[str]):
    def visit_binary_expr(self, expr: Binary) -> str:
        return "binary"

    def visit_call_expr(self, expr: Call) -> str:
        return "call"

    def visit_get_expr(self, expr: Get) -> str:
        return "get"

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return "group"

    def visit_literal_expr(self, expr: Literal) -> str:
        return "literal"

    def visit_set_expr(self, expr: Set) -> str:
        return "set"

    def visit_super_expr(self, expr: Super) -> str:
        return "super"

    def visit_this_expr(self, expr: This) -> str:
        return "this"

    def visit_unary_expr(self, expr: Unary) -> str:
        return "unary"

    def visit_variable_expr(self, expr: Variable) -> str:
        return "variable"

    def visit_assign_expr(self, expr: Assign) -> str:
        return "assign"

    def visit_logical_expr(self, expr: Logical) -> str:
        return "logical"

    def visit_conditional_expr(self, expr: Conditional) -> str:
        return "conditional"


class TestExpressions(unittest.TestCase):
    def setUp(self):
        self.visitor = Mock(spec=TestExprVisitor)
        self.token = Token(TokenType.IDENTIFIER, "test", None, 1)

    def test_get_expr(self):
        obj = Literal("object")
        expr = Get(obj, self.token)
        expr.accept(self.visitor)
        self.visitor.visit_get_expr.assert_called_once_with(expr)

    def test_set_expr(self):
        obj = Literal("object")
        value = Literal(42)
        expr = Set(obj, self.token, value)
        expr.accept(self.visitor)
        self.visitor.visit_set_expr.assert_called_once_with(expr)

    def test_super_expr(self):
        keyword = Token(TokenType.SUPER, "super", None, 1)
        expr = Super(keyword, self.token)
        expr.accept(self.visitor)
        self.visitor.visit_super_expr.assert_called_once_with(expr)

    def test_this_expr(self):
        keyword = Token(TokenType.THIS, "this", None, 1)
        expr = This(keyword)
        expr.accept(self.visitor)
        self.visitor.visit_this_expr.assert_called_once_with(expr)

    def test_conditional_expr(self):
        condition = Literal(True)
        then_branch = Literal(1)
        else_branch = Literal(0)
        expr = Conditional(condition, then_branch, else_branch)
        expr.accept(self.visitor)
        self.visitor.visit_conditional_expr.assert_called_once_with(expr)

    def test_visitor_implementation(self):
        visitor = TestExprVisitor()
        exprs = {
            Binary(Literal(1), self.token, Literal(2)): "binary",
            Call(Literal("fn"), self.token, []): "call",
            Get(Literal("obj"), self.token): "get",
            Grouping(Literal(1)): "group",
            Literal(42): "literal",
            Set(Literal("obj"), self.token, Literal(1)): "set",
            Super(self.token, self.token): "super",
            This(self.token): "this",
            Unary(self.token, Literal(1)): "unary",
            Variable(self.token): "variable",
            Assign(self.token, Literal(1)): "assign",
            Logical(Literal(True), self.token, Literal(False)): "logical",
            Conditional(Literal(True), Literal(1), Literal(0)): "conditional",
        }

        for expr, expected in exprs.items():
            with self.subTest(expr_type=type(expr).__name__):
                self.assertEqual(expr.accept(visitor), expected)


if __name__ == "__main__":
    unittest.main()
