from typing import TYPE_CHECKING, Any, List, override

from .environment import Environment
from .error_handler import ReturnException
from .lox_callable import LoxCallable
from .stmt import Function

if TYPE_CHECKING:
    from .interpreter import Interpreter
    from .lox_instance import LoxInstance


class LoxFunction(LoxCallable):
    def __init__(
        self, declaration: Function, closure: Environment, is_initializer: bool
    ) -> None:
        self.closure: Environment = closure
        self.declaration: Function = declaration
        self.is_initializer: bool = is_initializer

    def bind(self, instance: "LoxInstance") -> "LoxFunction":
        environment: Environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        environment: Environment = Environment(self.closure)

        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        try:
            interpreter._execute_block(self.declaration.body, environment)
        except ReturnException as e:
            return e.value

        if self.is_initializer:
            return self.closure.get_at(0, "this")

        return None

    @override
    def arity(self) -> int:
        return len(self.declaration.params)

    @override
    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"
