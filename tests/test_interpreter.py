import os
import sys
import unittest
from unittest.mock import Mock, patch

# Append the source directory to the system path
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")

from callable import LoxCallable
from environment import Environment
from error_handler import BreakException, LoxRuntimeError, ReturnException
from expr import Assign, Binary, Call, Grouping, Literal, Logical, Unary, Variable
from interpreter import Interpreter
from stmt import Block, Break, Expression, Function, If, Print, Return, Var, While
from tokens import Token, TokenType


class TestInterpreter(unittest.TestCase):
    def setUp(self):
        self.interpreter = Interpreter()
        self.environment = Environment()

    def test_literal_expr(self):
        expr = Literal(123)
        result = self.interpreter.visit_literal_expr(expr)
        self.assertEqual(result, 123)

    def test_grouping_expr(self):
        expr = Grouping(Literal(123))
        result = self.interpreter.visit_grouping_expr(expr)
        self.assertEqual(result, 123)

    def test_unary_expr(self):
        expr = Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123.0))
        result = self.interpreter.visit_unary_expr(expr)
        self.assertEqual(result, -123.0)

    def test_binary_expr(self):
        expr = Binary(Literal(1.0), Token(TokenType.PLUS, "+", None, 1), Literal(2.0))
        result = self.interpreter.visit_binary_expr(expr)
        self.assertEqual(result, 3.0)

    def test_variable_expr(self):
        self.interpreter.globals.define("x", 123)
        expr = Variable(name=Token(TokenType.IDENTIFIER, "x", None, 1))
        result = self.interpreter.visit_variable_expr(expr)
        self.assertEqual(result, 123)

    def test_assign_expr(self):
        self.interpreter.globals.define("x", None)
        expr = Assign(
            name=Token(TokenType.IDENTIFIER, "x", None, 1), value=Literal(value=123)
        )
        result = self.interpreter.visit_assign_expr(expr)
        self.assertEqual(result, 123)

    def test_logical_expr(self):
        expr = Logical(
            Literal(True), Token(TokenType.OR, "or", None, 1), Literal(False)
        )
        result = self.interpreter.visit_logical_expr(expr)
        self.assertTrue(result)

    def test_call_expr(self):
        with patch("callable.LoxCallable", spec=LoxCallable) as MockCallable:
            mock_callable = MockCallable.return_value
            mock_callable.arity.return_value = 0
            mock_callable.call.return_value = "called"
            callee = Mock()
            callee.accept.return_value = mock_callable
            expr = Call(callee, Token(TokenType.LEFT_PAREN, "(", None, 1), [])
            result = self.interpreter.visit_call_expr(expr)
            self.assertEqual(result, "called")

    def test_expression_stmt(self):
        expr = Literal(123)
        stmt = Expression(expr)
        with patch.object(
            self.interpreter, "_evaluate", return_value=123
        ) as mock_evaluate:
            self.interpreter.visit_expression_stmt(stmt)
            mock_evaluate.assert_called_once_with(expr)

    def test_print_stmt(self):
        expr = Literal(123)
        stmt = Print(expr)
        with patch("builtins.print") as mock_print:
            with patch.object(
                self.interpreter, "_evaluate", return_value=123
            ) as mock_evaluate:
                self.interpreter.visit_print_stmt(stmt)
                mock_evaluate.assert_called_once_with(expr)
                mock_print.assert_called_once_with("123")

    def test_var_stmt(self):
        name = Token(TokenType.IDENTIFIER, "x", None, 1)
        initializer = Literal(123)
        stmt = Var(name, initializer)
        with patch.object(
            self.interpreter, "_evaluate", return_value=123
        ) as mock_evaluate:
            self.interpreter.visit_var_stmt(stmt)
            mock_evaluate.assert_called_once_with(initializer)
            self.assertEqual(self.interpreter._environment.get(name), 123)

    def test_block_stmt(self):
        statements = [Mock(spec=Expression)]
        stmt = Block(statements)
        with patch.object(self.interpreter, "_execute") as mock_execute:
            self.interpreter.visit_block_stmt(stmt)
            mock_execute.assert_called_once_with(statements[0])

    def test_if_stmt(self):
        condition = Literal(True)
        then_branch = Mock(spec=Expression)
        else_branch = Mock(spec=Expression)
        stmt = If(condition, then_branch, else_branch)
        with patch.object(
            self.interpreter, "_evaluate", return_value=True
        ) as mock_evaluate:
            with patch.object(self.interpreter, "_execute") as mock_execute:
                self.interpreter.visit_if_stmt(stmt)
                mock_evaluate.assert_called_once_with(condition)
                mock_execute.assert_called_once_with(then_branch)

    def test_while_stmt(self):
        condition = Literal(True)
        body = Mock(spec=Expression)
        stmt = While(condition, body)
        with patch.object(
            self.interpreter, "_evaluate", side_effect=[True, False]
        ) as mock_evaluate:
            with patch.object(self.interpreter, "_execute") as mock_execute:
                self.interpreter.visit_while_stmt(stmt)
                self.assertEqual(mock_evaluate.call_count, 2)
                mock_execute.assert_called_once_with(body)

    def test_break_stmt(self):
        stmt = Break()
        with self.assertRaises(BreakException):
            self.interpreter.visit_break_stmt(stmt)

    def test_function_stmt(self):
        name = Token(TokenType.IDENTIFIER, "foo", None, 1)
        params = [Token(TokenType.IDENTIFIER, "x", None, 1)]
        body = [Mock(spec=Expression)]
        stmt = Function(name, params, body)
        with patch("function.LoxFunction") as MockFunction:
            mock_function = MockFunction.return_value
            self.interpreter.visit_function_stmt(stmt)
            self.assertEqual(self.interpreter._environment.get(name), mock_function)

    def test_return_stmt(self):
        keyword = Token(TokenType.RETURN, "return", None, 1)
        value = Literal(123)
        stmt = Return(keyword, value)
        with patch.object(
            self.interpreter, "_evaluate", return_value=123
        ) as mock_evaluate:
            with self.assertRaises(ReturnException) as context:
                self.interpreter.visit_return_stmt(stmt)
            mock_evaluate.assert_called_once_with(value)
            self.assertEqual(context.exception.value, 123)


if __name__ == "__main__":
    unittest.main()
