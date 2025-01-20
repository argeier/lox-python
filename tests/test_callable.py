import unittest
from time import time
from unittest.mock import Mock

from src.lox.lox_callable import ClockCallable


class TestClockCallable(unittest.TestCase):

    def setUp(self):
        self.clock_callable = ClockCallable()

    def test_call(self):
        interpreter = Mock()
        result = self.clock_callable.call(interpreter, [])
        self.assertIsInstance(result, float)
        self.assertAlmostEqual(result, time(), delta=1)

    def test_arity(self):
        self.assertEqual(self.clock_callable.arity(), 0)

    def test_str(self):
        self.assertEqual(str(self.clock_callable), "<native fn>")


if __name__ == "__main__":
    unittest.main()
