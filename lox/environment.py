from __future__ import annotations

from typing import Any, Dict, Optional

from .error_handler import LoxRuntimeError
from .tokens import Token


class Environment:
    """
    Represents a runtime environment for variable storage and scope management in the Lox interpreter.

    This class manages variable bindings within a particular scope and handles variable resolution,
    including support for nested (enclosing) environments to facilitate lexical scoping.

    Attributes:
        enclosing (Optional[Environment]): The parent environment that encloses the current scope.
            If `None`, this environment serves as the global scope.
        values (Dict[str, Any]): A dictionary mapping variable names to their corresponding values
            within the current environment.
    """

    __slots__ = ("enclosing", "values")

    def __init__(self, enclosing: Optional[Environment] = None) -> None:
        """
        Initialize a new Environment instance.

        Args:
            enclosing (Optional[Environment]): The enclosing (parent) environment. Defaults to None.
        """
        self.enclosing = enclosing
        self.values: Dict[str, Any] = {}

    def define(self, name: str, value: Any) -> None:
        """
        Define a new variable or update an existing variable in the current environment.

        Args:
            name (str): The name of the variable.
            value (Any): The value to assign to the variable.
        """
        self.values[name] = value

    def get(self, name: Token) -> Any:
        """
        Retrieve the value of a variable by its name.

        Args:
            name (Token): The token representing the variable's name.

        Returns:
            Any: The value of the variable.

        Raises:
            LoxRuntimeError: If the variable is undefined in the current or enclosing environments.
        """
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: Any) -> None:
        """
        Assign a new value to an existing variable.

        Args:
            name (Token): The token representing the variable's name.
            value (Any): The new value to assign to the variable.

        Raises:
            LoxRuntimeError: If the variable is undefined in the current or enclosing environments.
        """
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def _ancestor(self, distance: int) -> Environment:
        """
        Traverse up the chain of enclosing environments to find an ancestor at a specific distance.

        Args:
            distance (int): The number of environments to traverse upwards.

        Returns:
            Environment: The ancestor environment at the specified distance.

        Raises:
            AssertionError: If an enclosing environment does not exist at the specified distance.
        """
        environment: Environment = self
        for _ in range(distance):
            assert environment.enclosing is not None, "Enclosing environment is None."
            environment = environment.enclosing
        return environment

    def get_at(self, distance: int, name: str) -> Any:
        """
        Retrieve the value of a variable from an ancestor environment at a specific distance.

        Args:
            distance (int): The distance of the ancestor environment.
            name (str): The name of the variable.

        Returns:
            Any: The value of the variable.
        """
        ancestor = self._ancestor(distance)
        return ancestor.values.get(name)

    def assign_at(self, distance: int, name: Token, value: Any) -> None:
        """
        Assign a new value to a variable in an ancestor environment at a specific distance.

        Args:
            distance (int): The distance of the ancestor environment.
            name (Token): The token representing the variable's name.
            value (Any): The new value to assign to the variable.
        """
        ancestor = self._ancestor(distance)
        ancestor.values[name.lexeme] = value
