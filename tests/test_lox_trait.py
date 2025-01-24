import unittest
from unittest.mock import Mock

from lox.lox_function import LoxFunction
from lox.lox_trait import LoxTrait
from lox.tokens import Token, TokenType


class TestLoxTrait(unittest.TestCase):
    def setUp(self):
        self.name = Token(TokenType.IDENTIFIER, "TestTrait", None, 1)
        self.mock_method = Mock(spec=LoxFunction)
        self.methods = {"test_method": self.mock_method}
        self.trait = LoxTrait(self.name, self.methods)

    def test_trait_creation(self):
        self.assertEqual(self.trait.name, self.name)
        self.assertEqual(self.trait.methods, self.methods)

    def test_string_representation(self):
        self.assertEqual(str(self.trait), "<trait TokenType.IDENTIFIER TestTrait None>")

    def test_method_access(self):
        self.assertEqual(self.trait.methods["test_method"], self.mock_method)


if __name__ == "__main__":
    unittest.main()
