import unittest
from abc import ABC
from typing import Any, List
from unittest.mock import Mock

from lox.lox_callable import LoxCallable


class TestLoxCallable(unittest.TestCase):
    class TestCallableImpl(LoxCallable):
        def call(self, interpreter: Any, arguments: List[Any]) -> Any:
            return "test_result"

        def arity(self) -> int:
            return 1

        def __str__(self) -> str:
            return "<test callable>"

    def test_abstract_methods(self):
        with self.assertRaises(TypeError):
            LoxCallable()

        callable_impl = self.TestCallableImpl()
        self.assertEqual(callable_impl.call(None, []), "test_result")
        self.assertEqual(callable_impl.arity(), 1)
        self.assertEqual(str(callable_impl), "<test callable>")

    def test_call_method(self):
        callable_obj = self.TestCallableImpl()
        interpreter = Mock()
        result = callable_obj.call(interpreter, ["arg1"])
        self.assertEqual(result, "test_result")

    def test_arity_method(self):
        callable_obj = self.TestCallableImpl()
        self.assertEqual(callable_obj.arity(), 1)

    def test_str_method(self):
        callable_obj = self.TestCallableImpl()
        self.assertEqual(str(callable_obj), "<test callable>")


if __name__ == "__main__":
    unittest.main()
