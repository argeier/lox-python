import unittest

from lox.environment import Environment
from lox.error_handler import LoxRuntimeError
from lox.tokens import Token, TokenType


class TestEnvironment(unittest.TestCase):
    def setUp(self):
        self.global_env = Environment()
        self.local_env = Environment(self.global_env)
        self.inner_env = Environment(self.local_env)

    def test_define_and_get(self):
        token = Token(TokenType.IDENTIFIER, "x", None, 1)
        self.global_env.define("x", 42)
        self.assertEqual(self.global_env.get(token), 42)

    def test_undefined_variable(self):
        token = Token(TokenType.IDENTIFIER, "undefined", None, 1)
        with self.assertRaises(LoxRuntimeError) as context:
            self.global_env.get(token)
        self.assertIn("Undefined variable", str(context.exception))

    def test_assign_existing(self):
        token = Token(TokenType.IDENTIFIER, "x", None, 1)
        self.global_env.define("x", 42)
        self.global_env.assign(token, 100)
        self.assertEqual(self.global_env.get(token), 100)

    def test_assign_undefined(self):
        token = Token(TokenType.IDENTIFIER, "undefined", None, 1)
        with self.assertRaises(LoxRuntimeError) as context:
            self.global_env.assign(token, 42)
        self.assertIn("Undefined variable", str(context.exception))

    def test_nested_environments(self):
        self.global_env.define("global", 1)
        self.local_env.define("local", 2)
        self.inner_env.define("inner", 3)

        global_token = Token(TokenType.IDENTIFIER, "global", None, 1)
        local_token = Token(TokenType.IDENTIFIER, "local", None, 1)
        inner_token = Token(TokenType.IDENTIFIER, "inner", None, 1)

        self.assertEqual(self.inner_env.get(global_token), 1)
        self.assertEqual(self.inner_env.get(local_token), 2)
        self.assertEqual(self.inner_env.get(inner_token), 3)

    def test_ancestor_access(self):
        self.global_env.define("x", "global")
        self.assertEqual(self.inner_env._ancestor(2), self.global_env)
        self.assertEqual(self.inner_env._ancestor(1), self.local_env)
        self.assertEqual(self.inner_env._ancestor(0), self.inner_env)

    def test_get_at(self):
        self.global_env.define("x", "global")
        self.local_env.define("x", "local")
        self.inner_env.define("x", "inner")

        self.assertEqual(self.inner_env.get_at(2, "x"), "global")
        self.assertEqual(self.inner_env.get_at(1, "x"), "local")
        self.assertEqual(self.inner_env.get_at(0, "x"), "inner")

    def test_assign_at(self):
        self.global_env.define("x", "global")
        token = Token(TokenType.IDENTIFIER, "x", None, 1)

        self.inner_env.assign_at(2, token, "new_global")
        self.assertEqual(self.global_env.get(token), "new_global")

    def test_invalid_ancestor_distance(self):
        with self.assertRaises(AssertionError):
            self.inner_env._ancestor(4)


if __name__ == "__main__":
    unittest.main()
