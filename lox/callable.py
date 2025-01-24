from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    from .interpreter import Interpreter


class LoxCallable(ABC):
    """
    Abstract base class for callable entities in the Lox interpreter.

    This class defines the interface for objects that can be called as functions
    within the Lox language. It requires implementing the `call`, `arity`,
    and `__str__` methods.
    """

    __slots__ = ()

    @abstractmethod
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> Any:
        """
        Invoke the callable with the given interpreter and arguments.

        Args:
            interpreter (Interpreter): The interpreter instance executing the call.
            arguments (List[Any]): A list of arguments passed to the callable.

        Returns:
            Any: The result of the callable execution.
        """
        ...

    @abstractmethod
    def arity(self) -> int:
        """
        Retrieve the number of arguments the callable expects.

        Returns:
            int: The number of expected arguments.
        """
        ...

    @abstractmethod
    def __str__(self) -> str:
        """
        Get the string representation of the callable.

        Returns:
            str: The string representation.
        """
        ...
