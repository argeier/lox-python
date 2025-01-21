import unittest
from unittest.mock import patch

from lox.error_handler import ErrorHandler
from lox.expr import (
    Assign,
    Binary,
    Call,
    Grouping,
    Literal,
    Logical,
    Unary,
    Variable,
)
from lox.interpreter import Interpreter
from lox.resolver import FunctionType, Resolver
from lox.stmt import Block, Expression, Function, If, Print, Return, Var
from lox.tokens import Token, TokenType


class TestResolver(unittest.TestCase):
    def setUp(self):
        self.error_handler = ErrorHandler()
        self.interpreter = Interpreter()
        self.resolver = Resolver(self.interpreter, self.error_handler)

    def test_visit_block_stmt(self):
        stmt = Block(statements=[])
        with patch.object(
            self.resolver, "_begin_scope"
        ) as mock_begin_scope, patch.object(
            self.resolver, "_end_scope"
        ) as mock_end_scope:
            self.resolver.visit_block_stmt(stmt)
            mock_begin_scope.assert_called_once()
            mock_end_scope.assert_called_once()

    def test_visit_expression_stmt(self):
        expr = Literal(value=123)
        stmt = Expression(expression=expr)
        with patch.object(self.resolver, "resolve") as mock_resolve:
            self.resolver.visit_expression_stmt(stmt)
            mock_resolve.assert_called_once_with(expr)

    def test_visit_function_stmt(self):
        stmt = Function(
            name=Token(TokenType.IDENTIFIER, "test", None, 1), params=[], body=[]
        )
        with patch.object(self.resolver, "_declare") as mock_declare, patch.object(
            self.resolver, "_define"
        ) as mock_define, patch.object(
            self.resolver, "_resolve_function"
        ) as mock_resolve_function:
            self.resolver.visit_function_stmt(stmt)
            mock_declare.assert_called_once_with(stmt.name)
            mock_define.assert_called_once_with(stmt.name)
            mock_resolve_function.assert_called_once_with(stmt, FunctionType.FUNCTION)

    def test_visit_if_stmt(self):
        condition = Literal(value=True)
        then_branch = Print(expression=Literal(value="then"))
        stmt = If(condition=condition, then_branch=then_branch, else_branch=None)
        with patch.object(self.resolver, "resolve") as mock_resolve:
            self.resolver.visit_if_stmt(stmt)
            mock_resolve.assert_any_call(condition)
            mock_resolve.assert_any_call(then_branch)

    def test_visit_print_stmt(self):
        expr = Literal(value="test")
        stmt = Print(expression=expr)
        with patch.object(self.resolver, "resolve") as mock_resolve:
            self.resolver.visit_print_stmt(stmt)
            mock_resolve.assert_called_once_with(expr)

    def test_visit_return_stmt(self):
        stmt = Return(
            keyword=Token(TokenType.RETURN, "return", None, 1), value=Literal(value=123)
        )
        with patch.object(
            self.resolver.error_handler, "error"
        ) as mock_error, patch.object(self.resolver, "resolve") as mock_resolve:
            self.resolver.visit_return_stmt(stmt)
            mock_resolve.assert_called_once_with(stmt.value)
            if self.resolver.current_function == FunctionType.NONE:
                mock_error.assert_called_once_with(
                    stmt.keyword, "Cannot return from top-level code."
                )
            else:
                mock_error.assert_not_called()

    def test_visit_var_stmt(self):
        stmt = Var(
            name=Token(TokenType.IDENTIFIER, "test", None, 1),
            initializer=Literal(value=123),
        )
        with patch.object(self.resolver, "_declare") as mock_declare, patch.object(
            self.resolver, "_define"
        ) as mock_define, patch.object(self.resolver, "resolve") as mock_resolve:
            self.resolver.visit_var_stmt(stmt)
            mock_declare.assert_called_once_with(stmt.name)
            mock_define.assert_called_once_with(stmt.name)
            mock_resolve.assert_called_once_with(stmt.initializer)

    def test_visit_variable_expr(self):
        expr = Variable(name=Token(TokenType.IDENTIFIER, "test", None, 1))
        with patch.object(
            self.resolver, "_resolve_local"
        ) as mock_resolve_local, patch.object(
            self.resolver.error_handler, "error"
        ) as mock_error:
            self.resolver.visit_variable_expr(expr)
            mock_resolve_local.assert_called_once_with(expr, expr.name)
            mock_error.assert_not_called()

    def test_visit_assign_expr(self):
        expr = Assign(
            name=Token(TokenType.IDENTIFIER, "test", None, 1), value=Literal(value=123)
        )
        with patch.object(
            self.resolver, "_resolve_local"
        ) as mock_resolve_local, patch.object(self.resolver, "resolve") as mock_resolve:
            self.resolver.visit_assign_expr(expr)
            mock_resolve.assert_called_once_with(expr.value)
            mock_resolve_local.assert_called_once_with(expr, expr.name)

    def test_visit_binary_expr(self):
        expr = Binary(
            left=Literal(value=1),
            operator=Token(TokenType.PLUS, "+", None, 1),
            right=Literal(value=2),
        )
        with patch.object(self.resolver, "resolve") as mock_resolve:
            self.resolver.visit_binary_expr(expr)
            mock_resolve.assert_any_call(expr.left)
            mock_resolve.assert_any_call(expr.right)

    def test_visit_call_expr(self):
        expr = Call(
            callee=Literal(value="callee"),
            paren=Token(TokenType.LEFT_PAREN, "(", None, 1),
            arguments=[],
        )
        with patch.object(self.resolver, "resolve") as mock_resolve:
            self.resolver.visit_call_expr(expr)
            mock_resolve.assert_any_call(expr.callee)
            self.assertEqual(mock_resolve.call_count, 1)

    def test_visit_grouping_expr(self):
        expr = Grouping(expression=Literal(value=123))
        with patch.object(self.resolver, "resolve") as mock_resolve:
            self.resolver.visit_grouping_expr(expr)
            mock_resolve.assert_called_once_with(expr.expression)

    def test_visit_logical_expr(self):
        expr = Logical(
            left=Literal(value=True),
            operator=Token(TokenType.AND, "and", None, 1),
            right=Literal(value=False),
        )
        with patch.object(self.resolver, "resolve") as mock_resolve:
            self.resolver.visit_logical_expr(expr)
            mock_resolve.assert_any_call(expr.left)
            mock_resolve.assert_any_call(expr.right)

    def test_visit_unary_expr(self):
        expr = Unary(
            operator=Token(TokenType.MINUS, "-", None, 1), right=Literal(value=123)
        )
        with patch.object(self.resolver, "resolve") as mock_resolve:
            self.resolver.visit_unary_expr(expr)
            mock_resolve.assert_called_once_with(expr.right)


if __name__ == "__main__":
    unittest.main()
