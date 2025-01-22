from __future__ import annotations

from time import time
from typing import TYPE_CHECKING, Any, List, override
from random import uniform
from math import exp, log, sqrt, tanh, sin, cos

if TYPE_CHECKING:
    from .interpreter import Interpreter
    from .lox_array import LoxArray

from .callable import LoxCallable
from .tokens import Token, TokenType
from .error_handler import LoxRuntimeError


class ClockCallable(LoxCallable):
    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        return time()

    @override
    def arity(self) -> int:
        return 0

    @override
    def __str__(self) -> str:
        return "<native fn>"


class ArrayCallable(LoxCallable):
    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        from .lox_array import LoxArray  # Import here to avoid circular import

        size: int = int(float(arguments[0]))
        return LoxArray(size)

    @override
    def arity(self) -> int:
        return 1

    @override
    def __str__(self) -> str:
        return "<native fn>"


class MaxCallable(LoxCallable):
    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        if not all(isinstance(arg, (int, float)) for arg in arguments):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "max", None, 0),
                "All arguments to max() must be numbers.",
            )
        return float(max(arguments))

    @override
    def arity(self) -> int:
        return 2

    @override
    def __str__(self) -> str:
        return "<native fn max>"


class MinCallable(LoxCallable):
    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        if not all(isinstance(arg, (int, float)) for arg in arguments):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "min", None, 0),
                "All arguments to min() must be numbers.",
            )
        return float(min(arguments))

    @override
    def arity(self) -> int:
        return 2

    @override
    def __str__(self) -> str:
        return "<native fn min>"


class SumCallable(LoxCallable):
    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        array = arguments[0]
        if not hasattr(array, "elements"):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "sum", None, 0),
                "Argument to sum() must be an array.",
            )
        if not all(isinstance(elem, (int, float)) for elem in array.elements):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "sum", None, 0),
                "All array elements must be numbers.",
            )
        return float(sum(array.elements))

    @override
    def arity(self) -> int:
        return 1

    @override
    def __str__(self) -> str:
        return "<native fn sum>"


class RandomCallable(LoxCallable):
    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        return uniform(0, 1)

    @override
    def arity(self) -> int:
        return 0

    @override
    def __str__(self) -> str:
        return "<native fn random>"


class RandomRangeCallable(LoxCallable):
    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        if not all(isinstance(arg, (int, float)) for arg in arguments):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "random_range", None, 0),
                "Arguments to random_range() must be numbers.",
            )
        min_val, max_val = arguments
        return float(uniform(min_val, max_val))

    @override
    def arity(self) -> int:
        return 2

    @override
    def __str__(self) -> str:
        return "<native fn random_range>"


class AbsCallable(LoxCallable):
    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        if not isinstance(arguments[0], (int, float)):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "abs", None, 0),
                "Argument to abs() must be a number.",
            )
        return float(abs(arguments[0]))

    @override
    def arity(self) -> int:
        return 1

    @override
    def __str__(self) -> str:
        return "<native fn abs>"


class ExpCallable(LoxCallable):
    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        if not isinstance(arguments[0], (int, float)):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "exp", None, 0),
                "Argument to exp() must be a number.",
            )
        return float(exp(arguments[0]))

    @override
    def arity(self) -> int:
        return 1

    @override
    def __str__(self) -> str:
        return "<native fn exp>"


class LogCallable(LoxCallable):
    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        if not isinstance(arguments[0], (int, float)):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "log", None, 0),
                "Argument to log() must be a number.",
            )
        return float(log(arguments[0]))

    @override
    def arity(self) -> int:
        return 1

    @override
    def __str__(self) -> str:
        return "<native fn log>"


class SqrtCallable(LoxCallable):
    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        if not isinstance(arguments[0], (int, float)):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "sqrt", None, 0),
                "Argument to sqrt() must be a number.",
            )
        return float(sqrt(arguments[0]))

    @override
    def arity(self) -> int:
        return 1

    @override
    def __str__(self) -> str:
        return "<native fn sqrt>"


class PowCallable(LoxCallable):
    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        if not all(isinstance(arg, (int, float)) for arg in arguments):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "pow", None, 0),
                "All arguments to pow() must be numbers.",
            )
        return float(pow(arguments[0], arguments[1]))

    @override
    def arity(self) -> int:
        return 2

    @override
    def __str__(self) -> str:
        return "<native fn pow>"


class FloorCallable(LoxCallable):
    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        if not isinstance(arguments[0], (int, float)):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "floor", None, 0),
                "Argument to floor() must be a number.",
            )
        return float(int(arguments[0]))

    @override
    def arity(self) -> int:
        return 1

    @override
    def __str__(self) -> str:
        return "<native fn floor>"


class CeilCallable(LoxCallable):
    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        if not isinstance(arguments[0], (int, float)):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "ceil", None, 0),
                "Argument to ceil() must be a number.",
            )
        return float(-int(-arguments[0]))

    @override
    def arity(self) -> int:
        return 1

    @override
    def __str__(self) -> str:
        return "<native fn ceil>"


class TanhCallable(LoxCallable):
    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        if not isinstance(arguments[0], (int, float)):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "tanh", None, 0),
                "Argument to tanh() must be a number.",
            )
        return float(tanh(arguments[0]))

    @override
    def arity(self) -> int:
        return 1

    @override
    def __str__(self) -> str:
        return "<native fn tanh>"


class SinCallable(LoxCallable):
    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        if not isinstance(arguments[0], (int, float)):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "sin", None, 0),
                "Argument to sin() must be a number.",
            )
        return float(sin(arguments[0]))

    @override
    def arity(self) -> int:
        return 1

    @override
    def __str__(self) -> str:
        return "<native fn sin>"


class CosCallable(LoxCallable):
    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        if not isinstance(arguments[0], (int, float)):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "cos", None, 0),
                "Argument to cos() must be a number.",
            )
        return float(cos(arguments[0]))

    @override
    def arity(self) -> int:
        return 1

    @override
    def __str__(self) -> str:
        return "<native fn cos>"
