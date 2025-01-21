from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from .lox_class import LoxClass

from .error_handler import LoxRuntimeError
from .lox_function import LoxFunction
from .tokens import Token


class LoxInstance:
    def __init__(self, klass: "LoxClass") -> None:
        self.klass = klass
        self.fields = {}

    def get(self, name: Token) -> Any:
        if name in self.fields:
            return self.fields[name]

        method: LoxFunction = self.klass.find_method(name.lexeme)

        if method is not None:
            return method.bind(self)

        raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: Any) -> None:
        self.fields[name.lexeme] = value

    def __str__(self):
        return f"{self.klass.name} instance"
