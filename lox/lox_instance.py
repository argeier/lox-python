from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from .error_handler import LoxRuntimeError
from .lox_function import LoxFunction
from .tokens import Token

if TYPE_CHECKING:
    from .lox_class import LoxClass


class LoxInstance:
    """
    Represents an instance of a Lox class.

    This class manages the fields and methods of a Lox class instance, including
    property access and method binding. It interacts with the interpreter to
    retrieve and set instance properties.

    Attributes:
        klass (LoxClass): The class that this instance belongs to.
        fields (Dict[str, Any]): A dictionary storing the instance's fields and their values.
    """

    __slots__ = ("klass", "fields")

    def __init__(self, klass: Optional[LoxClass]) -> None:
        self.klass: Optional[LoxClass] = klass
        self.fields: Dict[str, Any] = {}

    def get(self, name: Token) -> Any:
        """
        Retrieves a property or method by name from the instance.

        Args:
            name (Token): The token representing the property name.

        Returns:
            Any: The value of the property or bound method.

        Raises:
            LoxRuntimeError: If the property is undefined.
        """
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        if self.klass is None:
            raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

        method = self.klass.find_method(name.lexeme)

        if method is not None and isinstance(method, LoxFunction):
            return method.bind(self)
        elif method is not None:
            return method

        raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: Any) -> None:
        """
        Sets a property on the instance.

        Args:
            name (Token): The token representing the property name.
            value (Any): The value to set for the property.
        """
        self.fields[name.lexeme] = value

    def __str__(self) -> str:
        """
        Returns the string representation of the clock function.

        Returns:
            str: The string representation.
        """
        assert self.klass is not None
        return f"{self.klass.name} instance"
