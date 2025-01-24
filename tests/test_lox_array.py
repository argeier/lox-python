import unittest
from unittest.mock import Mock, patch
from lox.lox_array import LoxArray, ArrayGetCallable, ArraySetCallable
from lox.tokens import Token, TokenType
from lox.error_handler import LoxRuntimeError


class TestLoxArray(unittest.TestCase):
    def setUp(self):
        self.array = LoxArray(3)
        self.token = lambda lexeme: Token(TokenType.IDENTIFIER, lexeme, None, 1)
        self.interpreter = Mock()

    def test_array_initialization(self):
        self.assertEqual(len(self.array.elements), 3)
        self.assertEqual(str(self.array), "[nil, nil, nil]")

    def test_get_array_length(self):
        length = self.array.get(self.token("length"))
        self.assertEqual(length, 3.0)

    def test_get_array_element(self):
        self.array.elements = [1.0, 2.0, 3.0]
        get_callable = self.array.get(self.token("get"))
        result = get_callable.call(self.interpreter, [1.0])
        self.assertEqual(result, 2.0)

    def test_set_array_element(self):
        set_callable = self.array.get(self.token("set"))
        result = set_callable.call(self.interpreter, [1.0, "test"])
        self.assertEqual(result, "test")
        self.assertEqual(self.array.elements[1], "test")

    def test_array_string_representation(self):
        self.array.elements = [1.0, None, "test"]
        self.assertEqual(str(self.array), "[1, nil, test]")

        self.array.elements = [1.5, 2.0, 3.0]
        self.assertEqual(str(self.array), "[1.5, 2, 3]")

    def test_get_invalid_property(self):
        with self.assertRaises(LoxRuntimeError):
            self.array.get(self.token("invalid"))

    def test_set_property_error(self):
        with self.assertRaises(LoxRuntimeError):
            self.array.set(self.token("any"), "value")

    def test_get_out_of_bounds(self):
        get_callable = self.array.get(self.token("get"))
        with self.assertRaises(LoxRuntimeError):
            get_callable.call(self.interpreter, [5.0])

    def test_set_out_of_bounds(self):
        set_callable = self.array.get(self.token("set"))
        with self.assertRaises(LoxRuntimeError):
            set_callable.call(self.interpreter, [5.0, "test"])

    def test_callable_string_representation(self):
        get_callable = ArrayGetCallable([])
        set_callable = ArraySetCallable([])
        self.assertEqual(str(get_callable), "<native fn>")
        self.assertEqual(str(set_callable), "<native fn>")

    def test_callable_arity(self):
        get_callable = ArrayGetCallable([])
        set_callable = ArraySetCallable([])
        self.assertEqual(get_callable.arity(), 1)
        self.assertEqual(set_callable.arity(), 2)

    def test_invalid_index_types(self):
        get_callable = self.array.get(self.token("get"))
        set_callable = self.array.get(self.token("set"))

        with self.assertRaises(LoxRuntimeError):
            get_callable.call(self.interpreter, ["invalid"])

        with self.assertRaises(LoxRuntimeError):
            set_callable.call(self.interpreter, ["invalid", "value"])


if __name__ == "__main__":
    unittest.main()
