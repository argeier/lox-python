from __future__ import annotations

from time import time
from typing import TYPE_CHECKING, Any, List, override

if TYPE_CHECKING:
    from .interpreter import Interpreter
    from .lox_array import LoxArray

from .callable import LoxCallable


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
