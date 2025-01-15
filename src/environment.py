from typing import Any, Dict, Optional

from error_handler import LoxRuntimeError
from tokens import Token


class Environment:

    def __init__(self, enclosing: "Environment | None" = None) -> None:
        self.enclosing = enclosing
        self.values: Dict[str, Any] = {}

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise LoxRuntimeError(name, f"Undefined variable {name.lexeme}.")

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return None

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return None

        raise LoxRuntimeError(name, f"Undefined variable {name.lexeme}.")
