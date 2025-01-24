from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, override

from .callable import LoxCallable
from .error_handler import LoxRuntimeError
from .lox_class import LoxClass
from .lox_instance import LoxInstance
from .tokens import Token, TokenType

if TYPE_CHECKING:
    from .interpreter import Interpreter


class ArrayGetCallable(LoxCallable):
    """
    Callable class to get an element from a LoxArray at a specified index.

    Attributes:
        elements (List[Any]): The list of elements in the array.
    """

    __slots__ = ("elements",)

    def __init__(self, elements: List[Any]) -> None:
        """
        Initialize the ArrayGetCallable with the array elements.

        Args:
            elements (List[Any]): The list of elements in the array.
        """
        self.elements = elements

    @override
    def arity(self) -> int:
        """
        Get the number of arguments the callable expects.

        Returns:
            int: The number of expected arguments (1 for index).
        """
        return 1

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> Any:
        """
        Retrieve the element at the specified index from the array.

        Args:
            interpreter (Interpreter): The interpreter instance executing the call.
            arguments (List[Any]): The list of arguments passed to the callable.

        Returns:
            Any: The element at the specified index.

        Raises:
            LoxRuntimeError: If the index is out of bounds.
        """
        try:
            index: int = int(float(arguments[0]))
            return self.elements[index]
        except (IndexError, TypeError, ValueError):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "get", None, 0),
                "Index out of bounds or invalid index type.",
            )

    @override
    def __str__(self) -> str:
        """
        Get the string representation of the callable.

        Returns:
            str: The string representation.
        """
        return "<native fn>"


class ArraySetCallable(LoxCallable):
    """
    Callable class to set an element in a LoxArray at a specified index.

    Attributes:
        elements (List[Any]): The list of elements in the array.
    """

    __slots__ = ("elements",)

    def __init__(self, elements: List[Any]) -> None:
        """
        Initialize the ArraySetCallable with the array elements.

        Args:
            elements (List[Any]): The list of elements in the array.
        """
        self.elements = elements

    @override
    def arity(self) -> int:
        """
        Get the number of arguments the callable expects.

        Returns:
            int: The number of expected arguments (2 for index and value).
        """
        return 2

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> Any:
        """
        Set the element at the specified index in the array to a new value.

        Args:
            interpreter (Interpreter): The interpreter instance executing the call.
            arguments (List[Any]): The list of arguments passed to the callable.

        Returns:
            Any: The value that was set.

        Raises:
            LoxRuntimeError: If the index is out of bounds.
        """
        try:
            index: int = int(float(arguments[0]))
            value: Any = arguments[1]
            self.elements[index] = value
            return value
        except (IndexError, TypeError, ValueError):
            raise LoxRuntimeError(
                Token(TokenType.IDENTIFIER, "set", None, 0),
                "Index out of bounds or invalid index type.",
            )

    @override
    def __str__(self) -> str:
        """
        Get the string representation of the callable.

        Returns:
            str: The string representation.
        """
        return "<native fn>"


class LoxArray(LoxInstance):
    """
    Represents an array instance in the Lox language.

    Attributes:
        elements (List[Any]): The list of elements contained in the array.
    """

    __slots__ = ("elements",)

    def __init__(self, size: int) -> None:
        """
        Initialize a LoxArray with a specified size.

        Args:
            size (int): The initial size of the array.
        """
        array_class: LoxClass = LoxClass(None, "Array", None, {})
        super().__init__(array_class)
        self.elements: List[Any] = [None] * size

    @override
    def get(self, name: Token) -> Any:
        """
        Retrieve a property from the array instance.

        Args:
            name (Token): The token representing the property's name.

        Returns:
            Any: The value of the property.

        Raises:
            LoxRuntimeError: If the property is undefined.
        """
        if name.lexeme == "get":
            return ArrayGetCallable(self.elements)
        elif name.lexeme == "set":
            return ArraySetCallable(self.elements)
        elif name.lexeme == "length":
            return float(len(self.elements))

        raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    @override
    def set(self, name: Token, value: Any) -> None:
        """
        Attempting to set a property on the array instance raises an error.

        Args:
            name (Token): The token representing the property's name.
            value (Any): The value to set.

        Raises:
            LoxRuntimeError: Always raised since array properties cannot be added.
        """
        raise LoxRuntimeError(name, "Can't add properties to arrays.")

    @override
    def __str__(self) -> str:
        """
        Get the string representation of the array.

        Returns:
            str: The string representation of the array elements.
        """
        return f"[{', '.join(self._stringify(elem) for elem in self.elements)}]"

    def _stringify(self, obj: Any) -> str:
        """
        Convert an object to its string representation.

        Args:
            obj (Any): The object to stringify.

        Returns:
            str: The string representation of the object.
        """
        if obj is None:
            return "nil"
        if isinstance(obj, float):
            return str(int(obj)) if obj.is_integer() else str(obj)
        return str(obj)
