import unittest
from unittest.mock import Mock, patch

from lox.error_handler import ErrorHandler
from lox.expr import (
    Assign,
    Binary,
    Call,
    Get,
    Grouping,
    Literal,
    Logical,
    Set,
    Super,
    This,
    Variable,
)
from lox.interpreter import Interpreter
from lox.resolver import FunctionType, ClassType, Resolver
from lox.stmt import (
    Block,
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


class TestResolver(unittest.TestCase):
    def setUp(self):
        self.interpreter = Interpreter()
        # Create a Mock instead of real ErrorHandler
        self.error_handler = Mock(spec=ErrorHandler)
        self.resolver = Resolver(self.interpreter, self.error_handler)

    def test_resolve_variable_declaration(self):
        stmt = Var(Token(TokenType.IDENTIFIER, "x", None, 1), Literal(42.0))
        self.resolver._begin_scope()
        self.resolver.visit_var_stmt(stmt)

        scope = self.resolver._scopes.peek()
        self.assertTrue(scope["x"])

    def test_resolve_variable_use_before_declaration(self):
        expr = Variable(Token(TokenType.IDENTIFIER, "x", None, 1))
        self.resolver._begin_scope()
        self.resolver._scopes.peek()["x"] = False

        self.resolver.visit_variable_expr(expr)
        self.error_handler.error.assert_called_once()

    def test_resolve_function_declaration(self):
        func = Function(
            Token(TokenType.IDENTIFIER, "test", None, 1),
            [Token(TokenType.IDENTIFIER, "param", None, 1)],
            [],
        )
        self.resolver._begin_scope()
        self.resolver.visit_function_stmt(func)

        scope = self.resolver._scopes.peek()
        self.assertTrue(scope["test"])

    def test_resolve_class_declaration(self):
        class_stmt = Class(
            Token(TokenType.IDENTIFIER, "TestClass", None, 1), None, [], [], []
        )
        self.resolver._begin_scope()
        self.resolver.visit_class_stmt(class_stmt)

        scope = self.resolver._scopes.peek()
        self.assertTrue(scope["TestClass"])
        self.assertEqual(self.resolver.current_class, ClassType.NONE)

    def test_resolve_class_with_super(self):
        superclass = Variable(Token(TokenType.IDENTIFIER, "Super", None, 1))
        class_stmt = Class(
            Token(TokenType.IDENTIFIER, "Sub", None, 1), superclass, [], [], []
        )

        self.resolver._begin_scope()
        self.resolver.visit_class_stmt(class_stmt)
        self.assertEqual(self.resolver.current_class, ClassType.NONE)

    def test_resolve_method_in_class(self):
        method = Function(Token(TokenType.IDENTIFIER, "method", None, 1), [], [])
        class_stmt = Class(
            Token(TokenType.IDENTIFIER, "TestClass", None, 1), None, [method], [], []
        )

        self.resolver._begin_scope()
        self.resolver.visit_class_stmt(class_stmt)
        self.assertEqual(self.resolver.current_class, ClassType.NONE)

    def test_resolve_this_in_class(self):
        this_expr = This(Token(TokenType.THIS, "this", None, 1))
        self.resolver.current_class = ClassType.CLASS
        self.resolver._begin_scope()
        self.resolver._scopes.peek()["this"] = True

        self.resolver.visit_this_expr(this_expr)

    def test_resolve_this_outside_class(self):
        this_expr = This(Token(TokenType.THIS, "this", None, 1))
        self.resolver.current_class = ClassType.NONE

        self.resolver.visit_this_expr(this_expr)
        self.error_handler.error.assert_called_once()

    def test_resolve_super(self):
        super_expr = Super(
            Token(TokenType.SUPER, "super", None, 1),
            Token(TokenType.IDENTIFIER, "method", None, 1),
        )
        self.resolver.current_class = ClassType.SUBCLASS
        self.resolver._begin_scope()
        self.resolver._scopes.peek()["super"] = True

        self.resolver.visit_super_expr(super_expr)

    def test_resolve_super_outside_class(self):
        super_expr = Super(
            Token(TokenType.SUPER, "super", None, 1),
            Token(TokenType.IDENTIFIER, "method", None, 1),
        )
        self.resolver.current_class = ClassType.NONE

        self.resolver.visit_super_expr(super_expr)
        self.error_handler.error.assert_called_once()

    def test_resolve_trait(self):
        trait_stmt = Trait(Token(TokenType.IDENTIFIER, "TestTrait", None, 1), [], [])
        self.resolver._begin_scope()
        self.resolver.visit_trait_stmt(trait_stmt)

        scope = self.resolver._scopes.peek()
        self.assertTrue(scope["TestTrait"])
        self.assertEqual(self.resolver.current_class, ClassType.NONE)

    def test_resolve_return_in_function(self):
        return_stmt = Return(Token(TokenType.RETURN, "return", None, 1), Literal(42.0))
        self.resolver.current_function = FunctionType.FUNCTION
        self.resolver.visit_return_stmt(return_stmt)

    def test_resolve_return_outside_function(self):
        return_stmt = Return(Token(TokenType.RETURN, "return", None, 1), Literal(42.0))
        self.resolver.current_function = FunctionType.NONE

        self.resolver.visit_return_stmt(return_stmt)
        self.error_handler.error.assert_called_once()

    def test_resolve_return_in_initializer(self):
        return_stmt = Return(Token(TokenType.RETURN, "return", None, 1), Literal(42.0))
        self.resolver.current_function = FunctionType.INITIALIZER

        self.resolver.visit_return_stmt(return_stmt)
        self.error_handler.error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
