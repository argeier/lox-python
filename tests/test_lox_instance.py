import unittest
from unittest.mock import Mock

from lox.error_handler import LoxRuntimeError
from lox.lox_function import LoxFunction
from lox.lox_instance import LoxInstance
from lox.tokens import Token, TokenType


class TestLoxInstance(unittest.TestCase):
    def setUp(self):
        self.klass = Mock()
        self.klass.name = "TestClass"
        self.instance = LoxInstance(self.klass)
        self.token = lambda lexeme: Token(TokenType.IDENTIFIER, lexeme, None, 1)

    def test_property_access(self):
        prop_token = self.token("test_prop")
        self.instance.set(prop_token, "value")
        self.assertEqual(self.instance.get(prop_token), "value")

    def test_undefined_property(self):
        self.klass.find_method.return_value = None
        with self.assertRaises(LoxRuntimeError):
            self.instance.get(self.token("undefined"))

    def test_method_binding(self):
        method = Mock(spec=LoxFunction)
        bound_method = Mock(spec=LoxFunction)
        method.bind.return_value = bound_method

        self.klass.find_method.return_value = method
        result = self.instance.get(self.token("test_method"))

        method.bind.assert_called_once_with(self.instance)
        self.assertEqual(result, bound_method)

    def test_nonfunction_method(self):
        method = Mock()
        self.klass.find_method.return_value = method

        result = self.instance.get(self.token("test_method"))
        self.assertEqual(result, method)

    def test_null_class(self):
        instance = LoxInstance(None)
        with self.assertRaises(LoxRuntimeError):
            instance.get(self.token("any"))

    def test_string_representation(self):
        self.assertEqual(str(self.instance), "TestClass instance")


if __name__ == "__main__":
    unittest.main()
