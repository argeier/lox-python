import unittest

from src.lox.environment import Environment
from src.lox.error_handler import LoxRuntimeError
from src.lox.tokens import Token, TokenType


class TestEnvironment(unittest.TestCase):

    def setUp(self):
        self.env = Environment()

    def test_define_and_get(self):
        token = Token(TokenType.IDENTIFIER, "a", None, 1)
        self.env.define("a", 42)
        self.assertEqual(self.env.get(token), 42)

    def test_get_undefined_variable(self):
        token = Token(TokenType.IDENTIFIER, "a", None, 1)
        with self.assertRaises(LoxRuntimeError) as context:
            self.env.get(token)
        self.assertEqual(str(context.exception), "Undefined variable a.")

    def test_assign_existing_variable(self):
        token = Token(TokenType.IDENTIFIER, "a", None, 1)
        self.env.define("a", 42)
        self.env.assign(token, 43)
        self.assertEqual(self.env.get(token), 43)

    def test_assign_undefined_variable(self):
        token = Token(TokenType.IDENTIFIER, "a", None, 1)
        with self.assertRaises(LoxRuntimeError) as context:
            self.env.assign(token, 43)
        self.assertEqual(str(context.exception), "Undefined variable a.")

    def test_enclosing_environment_get(self):
        enclosing_env = Environment()
        enclosing_env.define("a", 42)
        self.env = Environment(enclosing_env)
        token = Token(TokenType.IDENTIFIER, "a", None, 1)
        self.assertEqual(self.env.get(token), 42)

    def test_enclosing_environment_assign(self):
        enclosing_env = Environment()
        enclosing_env.define("a", 42)
        self.env = Environment(enclosing_env)
        token = Token(TokenType.IDENTIFIER, "a", None, 1)
        self.env.assign(token, 43)
        self.assertEqual(enclosing_env.get(token), 43)


if __name__ == "__main__":
    unittest.main()
