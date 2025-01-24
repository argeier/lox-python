import unittest
from math import cos, exp, log, sin, sqrt, tanh
from time import time
from unittest.mock import Mock, patch

from lox.error_handler import LoxRuntimeError
from lox.lox_callable import (
    AbsCallable,
    ArrayCallable,
    CeilCallable,
    ClockCallable,
    CosCallable,
    ExpCallable,
    FloorCallable,
    LogCallable,
    MaxCallable,
    MinCallable,
    PowCallable,
    RandomCallable,
    RandomRangeCallable,
    SinCallable,
    SqrtCallable,
    SumCallable,
    TanhCallable,
)
from lox.tokens import Token, TokenType


class TestLoxCallable(unittest.TestCase):
    def setUp(self):
        self.interpreter = Mock()

    def test_clock_callable(self):
        clock = ClockCallable()
        with patch("lox.lox_callable.time") as mock_time:
            mock_time.return_value = 12345.0
            result = clock.call(self.interpreter, [])
            self.assertEqual(result, 12345.0)
        self.assertEqual(clock.arity(), 0)
        self.assertEqual(str(clock), "<native fn>")

    def test_array_callable(self):
        array_fn = ArrayCallable()
        result = array_fn.call(self.interpreter, [3.0])
        self.assertEqual(len(result.elements), 3)
        self.assertEqual(array_fn.arity(), 1)
        self.assertEqual(str(array_fn), "<native fn>")

    def test_max_callable(self):
        max_fn = MaxCallable()
        result = max_fn.call(self.interpreter, [1.0, 2.0])
        self.assertEqual(result, 2.0)
        self.assertEqual(max_fn.arity(), 2)
        self.assertEqual(str(max_fn), "<native fn max>")

        with self.assertRaises(LoxRuntimeError):
            max_fn.call(self.interpreter, [1.0, "2"])

    def test_min_callable(self):
        min_fn = MinCallable()
        result = min_fn.call(self.interpreter, [1.0, 2.0])
        self.assertEqual(result, 1.0)
        self.assertEqual(min_fn.arity(), 2)
        self.assertEqual(str(min_fn), "<native fn min>")

        with self.assertRaises(LoxRuntimeError):
            min_fn.call(self.interpreter, [1.0, "2"])

    def test_sum_callable(self):
        sum_fn = SumCallable()
        mock_array = Mock()
        mock_array.elements = [1.0, 2.0, 3.0]
        result = sum_fn.call(self.interpreter, [mock_array])
        self.assertEqual(result, 6.0)
        self.assertEqual(sum_fn.arity(), 1)

        with self.assertRaises(LoxRuntimeError):
            sum_fn.call(self.interpreter, [1.0])

        mock_array.elements = [1.0, "2", 3.0]
        with self.assertRaises(LoxRuntimeError):
            sum_fn.call(self.interpreter, [mock_array])

    def test_random_callable(self):
        random_fn = RandomCallable()
        with patch("lox.lox_callable.uniform") as mock_uniform:
            mock_uniform.return_value = 0.5
            result = random_fn.call(self.interpreter, [])
            self.assertEqual(result, 0.5)
        self.assertEqual(random_fn.arity(), 0)

    def test_random_range_callable(self):
        random_range = RandomRangeCallable()
        with patch("lox.lox_callable.uniform") as mock_uniform:
            mock_uniform.return_value = 1.5
            result = random_range.call(self.interpreter, [1.0, 2.0])
            self.assertEqual(result, 1.5)
        self.assertEqual(random_range.arity(), 2)

        with self.assertRaises(LoxRuntimeError):
            random_range.call(self.interpreter, [1.0, "2"])

    def test_math_callables(self):
        test_cases = [
            (AbsCallable(), [-2.0], abs, "<native fn abs>"),
            (ExpCallable(), [2.0], exp, "<native fn exp>"),
            (LogCallable(), [2.0], log, "<native fn log>"),
            (SqrtCallable(), [4.0], sqrt, "<native fn sqrt>"),
            (PowCallable(), [2.0, 3.0], pow, "<native fn pow>"),
            (FloorCallable(), [2.5], lambda x: float(int(x)), "<native fn floor>"),
            (CeilCallable(), [2.5], lambda x: float(-int(-x)), "<native fn ceil>"),
            (TanhCallable(), [0.5], tanh, "<native fn tanh>"),
            (SinCallable(), [0.5], sin, "<native fn sin>"),
            (CosCallable(), [0.5], cos, "<native fn cos>"),
        ]

        for callable_obj, args, func, str_repr in test_cases:
            with self.subTest(callable_type=type(callable_obj).__name__):
                result = callable_obj.call(self.interpreter, args)
                expected = float(func(*args))
                self.assertEqual(result, expected)
                self.assertEqual(str(callable_obj), str_repr)

                if len(args) == 1:
                    with self.assertRaises(LoxRuntimeError):
                        callable_obj.call(self.interpreter, ["not a number"])
                else:
                    with self.assertRaises(LoxRuntimeError):
                        callable_obj.call(self.interpreter, [1.0, "not a number"])


if __name__ == "__main__":
    unittest.main()
