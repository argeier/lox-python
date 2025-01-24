from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, override

from .callable import LoxCallable
from .environment import Environment
from .error_handler import ReturnException
from .stmt import Function

if TYPE_CHECKING:
    from .interpreter import Interpreter
    from .lox_instance import LoxInstance


class LoxFunction(LoxCallable):
    """
    Represents a function in the Lox language.

    This class encapsulates a Lox function's declaration, its closure environment,
    and whether it is an initializer. It provides functionality to bind the function
    to an instance, determine if it's a getter, execute the function call, and
    retrieve its arity.

    Attributes:
        declaration (Function): The function's declaration statement.
        closure (Environment): The environment capturing the function's closure.
        is_initializer (bool): Indicates if the function is an initializer.
    """

    __slots__ = ("declaration", "closure", "is_initializer")

    def __init__(
        self, declaration: Function, closure: Environment, is_initializer: bool
    ) -> None:
        self.declaration: Function = declaration
        self.closure: Environment = closure
        self.is_initializer: bool = is_initializer

    def bind(self, instance: LoxInstance) -> LoxFunction:
        """
        Binds the function to a specific instance.

        Args:
            instance (LoxInstance): The instance to bind the function to.

        Returns:
            LoxFunction: A new function bound to the given instance.
        """
        environment: Environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

    def is_getter(self) -> bool:
        """
        Determines if the function is a getter.

        Returns:
            bool: True if the function is a getter, False otherwise.
        """
        return self.declaration.params is None

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> Any:
        """
        Executes the function with the given arguments.

        Args:
            interpreter (Interpreter): The interpreter instance.
            arguments (List[Any]): The arguments passed to the function.

        Returns:
            Any: The result of the function execution.
        """
        environment: Environment = Environment(self.closure)
        if self.declaration.params:
            for param, arg in zip(self.declaration.params, arguments):
                environment.define(param.lexeme, arg)

        try:
            interpreter._execute_block(self.declaration.body, environment)
        except ReturnException as e:
            return e.value

        if self.is_initializer:
            return self.closure.get_at(0, "this")

        return None

    @override
    def arity(self) -> int:
        """
        Returns the number of parameters the function expects.

        Returns:
            int: The arity of the function.
        """
        return len(self.declaration.params or [])

    @override
    def __str__(self) -> str:
        """
        Returns the string representation of the clock function.

        Returns:
            str: The string representation.
        """
        return f"<fn {self.declaration.name.lexeme}>"
