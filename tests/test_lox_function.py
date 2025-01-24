import unittest
from unittest.mock import Mock, patch

from lox.environment import Environment
from lox.error_handler import ReturnException
from lox.lox_function import LoxFunction
from lox.stmt import Function
from lox.tokens import Token, TokenType


class TestLoxFunction(unittest.TestCase):
    def setUp(self):
        self.interpreter = Mock()
        self.closure = Environment()
        self.token = lambda lexeme: Token(TokenType.IDENTIFIER, lexeme, None, 1)

        # Create a sample function declaration
        self.fn_name = self.token("test")
        self.params = [self.token("x"), self.token("y")]
        self.body = []
        self.declaration = Function(self.fn_name, self.params, self.body)

    def test_function_creation(self):
        function = LoxFunction(self.declaration, self.closure, False)
        self.assertEqual(function.arity(), 2)
        self.assertEqual(str(function), "<fn test>")

    def test_function_binding(self):
        function = LoxFunction(self.declaration, self.closure, False)
        instance = Mock()
        bound = function.bind(instance)

        self.assertNotEqual(bound.closure, function.closure)
        self.assertEqual(bound.closure.get(self.token("this")), instance)

    def test_getter_detection(self):
        getter_decl = Function(self.fn_name, None, self.body)
        getter = LoxFunction(getter_decl, self.closure, False)
        self.assertTrue(getter.is_getter())

        regular = LoxFunction(self.declaration, self.closure, False)
        self.assertFalse(regular.is_getter())

    def test_function_call(self):
        function = LoxFunction(self.declaration, self.closure, False)
        args = [1, 2]

        function.call(self.interpreter, args)

        self.interpreter._execute_block.assert_called_once_with(
            self.body, unittest.mock.ANY
        )
        env = self.interpreter._execute_block.call_args[0][1]
        self.assertEqual(env.get(self.token("x")), 1)
        self.assertEqual(env.get(self.token("y")), 2)

    def test_return_handling(self):
        function = LoxFunction(self.declaration, self.closure, False)

        self.interpreter._execute_block.side_effect = ReturnException("result")
        result = function.call(self.interpreter, [1, 2])

        self.assertEqual(result, "result")

    def test_initializer(self):
        function = LoxFunction(self.declaration, self.closure, True)
        this_obj = Mock()
        function.closure.define("this", this_obj)

        result = function.call(self.interpreter, [1, 2])
        self.assertEqual(result, this_obj)


if __name__ == "__main__":
    unittest.main()
