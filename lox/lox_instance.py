from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .lox_class import LoxClass

from .error_handler import LoxRuntimeError
from .lox_function import LoxFunction
from .tokens import Token


class LoxInstance:

    def __init__(self, klass: Optional[LoxClass]) -> None:
        self.klass: Optional[LoxClass] = klass
        self.fields: Dict[str, Any] = {}

    def get(self, name: Token) -> Any:
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
        self.fields[name.lexeme] = value

    def __str__(self):
        return f"{self.klass.name} instance"
