import unittest
from unittest.mock import Mock, patch

from lox.environment import Environment
from lox.error_handler import BreakException, LoxRuntimeError, ReturnException
from lox.expr import (
    Assign,
    Binary,
    Call,
    Conditional,
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
from lox.interpreter import Interpreter
from lox.lox_callable import LoxCallable
from lox.lox_class import LoxClass
from lox.lox_instance import LoxInstance
from lox.stmt import (
    Block,
    Break,
    Class,
    Expression,
    Function,
    If,
    Print,
    Return,
    Trait,
    Var,
    While,
)
from lox.tokens import Token, TokenType


class TestInterpreter(unittest.TestCase):
    def setUp(self):
        self.interpreter = Interpreter()
        self.environment = Environment()

    def test_literal_expr(self):
        expr = Literal(123.0)
        result = self.interpreter.visit_literal_expr(expr)
        self.assertEqual(result, 123.0)

        expr = Literal("test")
        result = self.interpreter.visit_literal_expr(expr)
        self.assertEqual(result, "test")

    def test_binary_expr_arithmetic(self):
        cases = [
            (1.0, TokenType.PLUS, 2.0, 3.0),
            (5.0, TokenType.MINUS, 3.0, 2.0),
            (4.0, TokenType.STAR, 2.0, 8.0),
            (8.0, TokenType.SLASH, 2.0, 4.0),
            (5.0, TokenType.MODULO, 2.0, 1.0),
        ]

        for left, op_type, right, expected in cases:
            expr = Binary(
                Literal(left), Token(op_type, op_type.value, None, 1), Literal(right)
            )
            result = self.interpreter.visit_binary_expr(expr)
            self.assertEqual(result, expected)

    def test_binary_expr_comparison(self):
        cases = [
            (1.0, TokenType.LESS, 2.0, True),
            (2.0, TokenType.GREATER, 1.0, True),
            (2.0, TokenType.LESS_EQUAL, 2.0, True),
            (2.0, TokenType.GREATER_EQUAL, 2.0, True),
            (2.0, TokenType.EQUAL_EQUAL, 2.0, True),
            (2.0, TokenType.BANG_EQUAL, 1.0, True),
        ]

        for left, op_type, right, expected in cases:
            expr = Binary(
                Literal(left), Token(op_type, op_type.value, None, 1), Literal(right)
            )
            result = self.interpreter.visit_binary_expr(expr)
            self.assertEqual(result, expected)

    def test_binary_expr_string_operations(self):
        expr = Binary(
            Literal("Hello"), Token(TokenType.PLUS, "+", None, 1), Literal(" World")
        )
        result = self.interpreter.visit_binary_expr(expr)
        self.assertEqual(result, "Hello World")

        expr = Binary(Literal("abc"), Token(TokenType.STAR, "*", None, 1), Literal(3.0))
        result = self.interpreter.visit_binary_expr(expr)
        self.assertEqual(result, "abcabcabc")

    def test_unary_expr(self):
        expr = Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123.0))
        result = self.interpreter.visit_unary_expr(expr)
        self.assertEqual(result, -123.0)

        expr = Unary(Token(TokenType.BANG, "!", None, 1), Literal(True))
        result = self.interpreter.visit_unary_expr(expr)
        self.assertEqual(result, False)

    def test_variable_definition_and_access(self):
        # Test variable definition
        var_name = Token(TokenType.IDENTIFIER, "x", None, 1)
        var_stmt = Var(var_name, Literal(42.0))
        self.interpreter.visit_var_stmt(var_stmt)

        # Test variable access
        var_expr = Variable(var_name)
        result = self.interpreter.visit_variable_expr(var_expr)
        self.assertEqual(result, 42.0)

    def test_assignment(self):
        # First define a variable
        var_name = Token(TokenType.IDENTIFIER, "x", None, 1)
        self.interpreter.globals.define("x", None)

        # Then test assignment
        assign_expr = Assign(var_name, Literal(100.0))
        result = self.interpreter.visit_assign_expr(assign_expr)
        self.assertEqual(result, 100.0)

        # Verify the assignment took effect
        var_expr = Variable(var_name)
        result = self.interpreter.visit_variable_expr(var_expr)
        self.assertEqual(result, 100.0)

    def test_block_statements(self):
        # Define variable in the global environment
        var_name = Token(TokenType.IDENTIFIER, "x", None, 1)
        self.interpreter.globals.define("x", None)

        statements = [Var(var_name, Literal(42.0)), Expression(Variable(var_name))]
        block = Block(statements)
        self.interpreter.visit_block_stmt(block)

    def test_if_statement(self):
        then_branch = Mock(spec=Expression)
        else_branch = Mock(spec=Expression)

        # Test true condition
        if_stmt = If(Literal(True), then_branch, else_branch)
        with patch.object(self.interpreter, "_execute") as mock_execute:
            self.interpreter.visit_if_stmt(if_stmt)
            mock_execute.assert_called_once_with(then_branch)

        # Test false condition
        if_stmt = If(Literal(False), then_branch, else_branch)
        with patch.object(self.interpreter, "_execute") as mock_execute:
            self.interpreter.visit_if_stmt(if_stmt)
            mock_execute.assert_called_once_with(else_branch)

    def test_logical_expressions(self):
        # Test OR with truthy first operand
        expr = Logical(
            Literal(True), Token(TokenType.OR, "or", None, 1), Literal(False)
        )
        result = self.interpreter.visit_logical_expr(expr)
        self.assertTrue(result)

        # Test AND with truthy first operand
        expr = Logical(
            Literal(True), Token(TokenType.AND, "and", None, 1), Literal(False)
        )
        result = self.interpreter.visit_logical_expr(expr)
        self.assertFalse(result)

    def test_while_statement(self):
        condition = Mock()
        body = Mock(spec=Expression)

        condition.accept.side_effect = [True, True, False]
        stmt = While(condition, body)

        with patch.object(self.interpreter, "_execute") as mock_execute:
            self.interpreter.visit_while_stmt(stmt)
            self.assertEqual(mock_execute.call_count, 2)

    def test_break_statement(self):
        with self.assertRaises(BreakException):
            self.interpreter.visit_break_stmt(Break())

    def test_function_declaration_and_call(self):
        func_name = Token(TokenType.IDENTIFIER, "test_func", None, 1)
        param = Token(TokenType.IDENTIFIER, "x", None, 1)

        self.interpreter.globals.define("x", 42.0)

        body = [Return(Token(TokenType.RETURN, "return", None, 1), Variable(param))]
        func_stmt = Function(func_name, [param], body)

        self.interpreter.visit_function_stmt(func_stmt)

        func_var = Variable(func_name)
        call_expr = Call(
            func_var, Token(TokenType.LEFT_PAREN, "(", None, 1), [Literal(42.0)]
        )

        result = self.interpreter.visit_call_expr(call_expr)
        self.assertEqual(result, 42.0)

    def test_division_by_zero(self):
        expr = Binary(Literal(1.0), Token(TokenType.SLASH, "/", None, 1), Literal(0.0))
        with self.assertRaises(LoxRuntimeError):
            self.interpreter.visit_binary_expr(expr)


if __name__ == "__main__":
    unittest.main()
