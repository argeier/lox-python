import unittest
from lox.callable import LoxCallable


class TestLoxCallable(unittest.TestCase):
    def test_cannot_instantiate_abstract(self):
        with self.assertRaises(TypeError):
            LoxCallable()

    def test_must_implement_abstract_methods(self):
        class IncompleteCallable(LoxCallable):
            pass

        with self.assertRaises(TypeError):
            IncompleteCallable()

    def test_concrete_implementation(self):
        class ConcreteCallable(LoxCallable):
            def call(self, interpreter, arguments):
                return "result"

            def arity(self):
                return 0

            def __str__(self):
                return "ConcreteCallable"

        callable_obj = ConcreteCallable()
        self.assertEqual(callable_obj.call(None, []), "result")
        self.assertEqual(callable_obj.arity(), 0)
        self.assertEqual(str(callable_obj), "ConcreteCallable")


if __name__ == "__main__":
    unittest.main()
