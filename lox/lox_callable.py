from __future__ import annotations

from math import cos, exp, log, sin, sqrt, tanh
from random import uniform
from time import time
from typing import TYPE_CHECKING, Any, List, Optional, override

from .callable import LoxCallable
from .error_handler import LoxRuntimeError
from .lox_array import LoxArray
from .tokens import Token, TokenType

if TYPE_CHECKING:
    from .interpreter import Interpreter


class ClockCallable(LoxCallable):
    """
    ClockCallable.

    Provides a native function to retrieve the current system time.
    """

    __slots__ = ()

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> float:
        """
        Executes the clock function to return the current system time.

        Args:
            interpreter (Interpreter): The interpreter instance.
            arguments (List[Any]): A list of arguments (expected to be empty).

        Returns:
            float: The current system time.
        """
        return time()

    @override
    def arity(self) -> int:
        """
        Returns the number of arguments the clock function accepts.

        Returns:
            int: The arity of the function (0).
        """
        return 0

    @override
    def __str__(self) -> str:
        """
        Returns the string representation of the clock function.

        Returns:
            str: The string representation.
        """
        return "<native fn>"


class ArrayCallable(LoxCallable):
    """
    ArrayCallable.

    Provides a native function to create a new LoxArray of a specified size.
    """

    __slots__ = ()

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> LoxArray:
        """
        Executes the array function to create a new LoxArray.

        Args:
            interpreter (Interpreter): The interpreter instance.
            arguments (List[Any]): A list containing the size of the array.

        Returns:
            LoxArray: A new LoxArray instance with the specified size.
        """
        size: int = int(float(arguments[0]))
        return LoxArray(size)

    @override
    def arity(self) -> int:
        """
        Returns the number of arguments the array function accepts.

        Returns:
            int: The arity of the function (1).
        """
        return 1

    @override
    def __str__(self) -> str:
        """
        Returns the string representation of the array function.

        Returns:
            str: The string representation.
        """
        return "<native fn>"


class MaxCallable(LoxCallable):
    """
    MaxCallable.

    Provides a native function to compute the maximum of two numerical arguments.
    """

    __slots__ = ()

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> float:
        """
        Executes the max function to determine the maximum value.

        Args:
            interpreter (Interpreter): The interpreter instance.
            arguments (List[Any]): A list containing two numerical arguments.

        Raises:
            LoxRuntimeError: If any argument is not a number.

        Returns:
            float: The maximum value among the arguments.
        """
        if not all(isinstance(arg, (int, float)) for arg in arguments):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "max", None, 0),
                "All arguments to max() must be numbers.",
            )
        return float(max(arguments))

    @override
    def arity(self) -> int:
        """
        Returns the number of arguments the max function accepts.

        Returns:
            int: The arity of the function (2).
        """
        return 2

    @override
    def __str__(self) -> str:
        """
        Returns the string representation of the max function.

        Returns:
            str: The string representation.
        """
        return "<native fn max>"


class MinCallable(LoxCallable):
    """
    MinCallable.

    Provides a native function to compute the minimum of two numerical arguments.
    """

    __slots__ = ()

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> float:
        """
        Executes the min function to determine the minimum value.

        Args:
            interpreter (Interpreter): The interpreter instance.
            arguments (List[Any]): A list containing two numerical arguments.

        Raises:
            LoxRuntimeError: If any argument is not a number.

        Returns:
            float: The minimum value among the arguments.
        """
        if not all(isinstance(arg, (int, float)) for arg in arguments):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "min", None, 0),
                "All arguments to min() must be numbers.",
            )
        return float(min(arguments))

    @override
    def arity(self) -> int:
        """
        Returns the number of arguments the min function accepts.

        Returns:
            int: The arity of the function (2).
        """
        return 2

    @override
    def __str__(self) -> str:
        """
        Returns the string representation of the min function.

        Returns:
            str: The string representation.
        """
        return "<native fn min>"


class SumCallable(LoxCallable):
    """
    SumCallable.

    Provides a native function to calculate the sum of all numerical elements in an array.
    """

    __slots__ = ()

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> float:
        """
        Executes the sum function to calculate the total of array elements.

        Args:
            interpreter (Interpreter): The interpreter instance.
            arguments (List[Any]): A list containing one array argument.

        Raises:
            LoxRuntimeError: If the argument is not an array or contains non-numerical elements.

        Returns:
            float: The sum of the array elements.
        """
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
        """
        Returns the number of arguments the sum function accepts.

        Returns:
            int: The arity of the function (1).
        """
        return 1

    @override
    def __str__(self) -> str:
        """
        Returns the string representation of the sum function.

        Returns:
            str: The string representation.
        """
        return "<native fn sum>"


class RandomCallable(LoxCallable):
    """
    RandomCallable.

    Provides a native function to generate a random float between 0 and 1.
    """

    __slots__ = ()

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> float:
        """
        Executes the random function to generate a random float.

        Args:
            interpreter (Interpreter): The interpreter instance.
            arguments (List[Any]): A list of arguments (expected to be empty).

        Returns:
            float: A random float between 0 and 1.
        """
        return uniform(0, 1)

    @override
    def arity(self) -> int:
        """
        Returns the number of arguments the random function accepts.

        Returns:
            int: The arity of the function (0).
        """
        return 0

    @override
    def __str__(self) -> str:
        """
        Returns the string representation of the random function.

        Returns:
            str: The string representation.
        """
        return "<native fn random>"


class RandomRangeCallable(LoxCallable):
    """
    RandomRangeCallable.

    Provides a native function to generate a random float within a specified range.
    """

    __slots__ = ()

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> float:
        """
        Executes the random_range function to generate a random float within a range.

        Args:
            interpreter (Interpreter): The interpreter instance.
            arguments (List[Any]): A list containing two numerical arguments (min and max).

        Raises:
            LoxRuntimeError: If any argument is not a number.

        Returns:
            float: A random float between min_val and max_val.
        """
        if not all(isinstance(arg, (int, float)) for arg in arguments):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "random_range", None, 0),
                "Arguments to random_range() must be numbers.",
            )
        min_val, max_val = arguments
        return float(uniform(min_val, max_val))

    @override
    def arity(self) -> int:
        """
        Returns the number of arguments the random_range function accepts.

        Returns:
            int: The arity of the function (2).
        """
        return 2

    @override
    def __str__(self) -> str:
        """
        Returns the string representation of the random_range function.

        Returns:
            str: The string representation.
        """
        return "<native fn random_range>"


class AbsCallable(LoxCallable):
    """
    AbsCallable.

    Provides a native function to calculate the absolute value of a number.
    """

    __slots__ = ()

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> float:
        """
        Executes the abs function to compute the absolute value.

        Args:
            interpreter (Interpreter): The interpreter instance.
            arguments (List[Any]): A list containing one numerical argument.

        Raises:
            LoxRuntimeError: If the argument is not a number.

        Returns:
            float: The absolute value of the argument.
        """
        if not isinstance(arguments[0], (int, float)):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "abs", None, 0),
                "Argument to abs() must be a number.",
            )
        return float(abs(arguments[0]))

    @override
    def arity(self) -> int:
        """
        Returns the number of arguments the abs function accepts.

        Returns:
            int: The arity of the function (1).
        """
        return 1

    @override
    def __str__(self) -> str:
        """
        Returns the string representation of the abs function.

        Returns:
            str: The string representation.
        """
        return "<native fn abs>"


class ExpCallable(LoxCallable):
    """
    ExpCallable.

    Provides a native function to calculate the exponential of a number.
    """

    __slots__ = ()

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> float:
        """
        Executes the exp function to compute the exponential.

        Args:
            interpreter (Interpreter): The interpreter instance.
            arguments (List[Any]): A list containing one numerical argument.

        Raises:
            LoxRuntimeError: If the argument is not a number.

        Returns:
            float: The exponential of the argument.
        """
        if not isinstance(arguments[0], (int, float)):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "exp", None, 0),
                "Argument to exp() must be a number.",
            )
        return float(exp(arguments[0]))

    @override
    def arity(self) -> int:
        """
        Returns the number of arguments the exp function accepts.

        Returns:
            int: The arity of the function (1).
        """
        return 1

    @override
    def __str__(self) -> str:
        """
        Returns the string representation of the exp function.

        Returns:
            str: The string representation.
        """
        return "<native fn exp>"


class LogCallable(LoxCallable):
    """
    LogCallable.

    Provides a native function to calculate the natural logarithm of a number.
    """

    __slots__ = ()

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> float:
        """
        Executes the log function to compute the natural logarithm.

        Args:
            interpreter (Interpreter): The interpreter instance.
            arguments (List[Any]): A list containing one numerical argument.

        Raises:
            LoxRuntimeError: If the argument is not a number.

        Returns:
            float: The natural logarithm of the argument.
        """
        if not isinstance(arguments[0], (int, float)):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "log", None, 0),
                "Argument to log() must be a number.",
            )
        return float(log(arguments[0]))

    @override
    def arity(self) -> int:
        """
        Returns the number of arguments the log function accepts.

        Returns:
            int: The arity of the function (1).
        """
        return 1

    @override
    def __str__(self) -> str:
        """
        Returns the string representation of the log function.

        Returns:
            str: The string representation.
        """
        return "<native fn log>"


class SqrtCallable(LoxCallable):
    """
    SqrtCallable.

    Provides a native function to calculate the square root of a number.
    """

    __slots__ = ()

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> float:
        """
        Executes the sqrt function to compute the square root.

        Args:
            interpreter (Interpreter): The interpreter instance.
            arguments (List[Any]): A list containing one numerical argument.

        Raises:
            LoxRuntimeError: If the argument is not a number.

        Returns:
            float: The square root of the argument.
        """
        if not isinstance(arguments[0], (int, float)):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "sqrt", None, 0),
                "Argument to sqrt() must be a number.",
            )
        return float(sqrt(arguments[0]))

    @override
    def arity(self) -> int:
        """
        Returns the number of arguments the sqrt function accepts.

        Returns:
            int: The arity of the function (1).
        """
        return 1

    @override
    def __str__(self) -> str:
        """
        Returns the string representation of the sqrt function.

        Returns:
            str: The string representation.
        """
        return "<native fn sqrt>"


class PowCallable(LoxCallable):
    """
    PowCallable.

    Provides a native function to raise a number to the power of another number.
    """

    __slots__ = ()

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> float:
        """
        Executes the pow function to compute exponentiation.

        Args:
            interpreter (Interpreter): The interpreter instance.
            arguments (List[Any]): A list containing two numerical arguments.

        Raises:
            LoxRuntimeError: If any argument is not a number.

        Returns:
            float: The result of raising the first argument to the power of the second.
        """
        if not all(isinstance(arg, (int, float)) for arg in arguments):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "pow", None, 0),
                "All arguments to pow() must be numbers.",
            )
        return float(pow(arguments[0], arguments[1]))

    @override
    def arity(self) -> int:
        """
        Returns the number of arguments the pow function accepts.

        Returns:
            int: The arity of the function (2).
        """
        return 2

    @override
    def __str__(self) -> str:
        """
        Returns the string representation of the pow function.

        Returns:
            str: The string representation.
        """
        return "<native fn pow>"


class FloorCallable(LoxCallable):
    """
    FloorCallable.

    Provides a native function to calculate the floor of a number.
    """

    __slots__ = ()

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> float:
        """
        Executes the floor function to compute the floor of a number.

        Args:
            interpreter (Interpreter): The interpreter instance.
            arguments (List[Any]): A list containing one numerical argument.

        Raises:
            LoxRuntimeError: If the argument is not a number.

        Returns:
            float: The floor of the argument.
        """
        if not isinstance(arguments[0], (int, float)):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "floor", None, 0),
                "Argument to floor() must be a number.",
            )
        return float(int(arguments[0]))

    @override
    def arity(self) -> int:
        """
        Returns the number of arguments the floor function accepts.

        Returns:
            int: The arity of the function (1).
        """
        return 1

    @override
    def __str__(self) -> str:
        """
        Returns the string representation of the floor function.

        Returns:
            str: The string representation.
        """
        return "<native fn floor>"


class CeilCallable(LoxCallable):
    """
    CeilCallable.

    Provides a native function to calculate the ceiling of a number.
    """

    __slots__ = ()

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> float:
        """
        Executes the ceil function to compute the ceiling of a number.

        Args:
            interpreter (Interpreter): The interpreter instance.
            arguments (List[Any]): A list containing one numerical argument.

        Raises:
            LoxRuntimeError: If the argument is not a number.

        Returns:
            float: The ceiling of the argument.
        """
        if not isinstance(arguments[0], (int, float)):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "ceil", None, 0),
                "Argument to ceil() must be a number.",
            )
        return float(-int(-arguments[0]))

    @override
    def arity(self) -> int:
        """
        Returns the number of arguments the ceil function accepts.

        Returns:
            int: The arity of the function (1).
        """
        return 1

    @override
    def __str__(self) -> str:
        """
        Returns the string representation of the ceil function.

        Returns:
            str: The string representation.
        """
        return "<native fn ceil>"


class TanhCallable(LoxCallable):
    """
    TanhCallable.

    Provides a native function to calculate the hyperbolic tangent of a number.
    """

    __slots__ = ()

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> float:
        """
        Executes the tanh function to compute the hyperbolic tangent.

        Args:
            interpreter (Interpreter): The interpreter instance.
            arguments (List[Any]): A list containing one numerical argument.

        Raises:
            LoxRuntimeError: If the argument is not a number.

        Returns:
            float: The hyperbolic tangent of the argument.
        """
        if not isinstance(arguments[0], (int, float)):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "tanh", None, 0),
                "Argument to tanh() must be a number.",
            )
        return float(tanh(arguments[0]))

    @override
    def arity(self) -> int:
        """
        Returns the number of arguments the tanh function accepts.

        Returns:
            int: The arity of the function (1).
        """
        return 1

    @override
    def __str__(self) -> str:
        """
        Returns the string representation of the tanh function.

        Returns:
            str: The string representation.
        """
        return "<native fn tanh>"


class SinCallable(LoxCallable):
    """
    SinCallable.

    Provides a native function to calculate the sine of a number.
    """

    __slots__ = ()

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> float:
        """
        Executes the sin function to compute the sine of a number.

        Args:
            interpreter (Interpreter): The interpreter instance.
            arguments (List[Any]): A list containing one numerical argument.

        Raises:
            LoxRuntimeError: If the argument is not a number.

        Returns:
            float: The sine of the argument.
        """
        if not isinstance(arguments[0], (int, float)):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "sin", None, 0),
                "Argument to sin() must be a number.",
            )
        return float(sin(arguments[0]))

    @override
    def arity(self) -> int:
        """
        Returns the number of arguments the sin function accepts.

        Returns:
            int: The arity of the function (1).
        """
        return 1

    @override
    def __str__(self) -> str:
        """
        Returns the string representation of the sin function.

        Returns:
            str: The string representation.
        """
        return "<native fn sin>"


class CosCallable(LoxCallable):
    """
    CosCallable.

    Provides a native function to calculate the cosine of a number.
    """

    __slots__ = ()

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> float:
        """
        Executes the cos function to compute the cosine of a number.

        Args:
            interpreter (Interpreter): The interpreter instance.
            arguments (List[Any]): A list containing one numerical argument.

        Raises:
            LoxRuntimeError: If the argument is not a number.

        Returns:
            float: The cosine of the argument.
        """
        if not isinstance(arguments[0], (int, float)):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "cos", None, 0),
                "Argument to cos() must be a number.",
            )
        return float(cos(arguments[0]))

    @override
    def arity(self) -> int:
        """
        Returns the number of arguments the cos function accepts.

        Returns:
            int: The arity of the function (1).
        """
        return 1

    @override
    def __str__(self) -> str:
        """
        Returns the string representation of the cos function.

        Returns:
            str: The string representation.
        """
        return "<native fn cos>"
