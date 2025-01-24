from __future__ import annotations

from typing import Any, Dict, Optional

from .error_handler import LoxRuntimeError
from .tokens import Token


class Environment:

    def __init__(self, enclosing: Optional[Environment] = None) -> None:
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

    def _ancestor(self, distance: int) -> Environment:
        environment: "Environment" = self
        for _ in range(distance):
            assert environment.enclosing is not None, "Enclosing environment is None."
            environment = environment.enclosing
        return environment

    def get_at(self, distance: int, name: str) -> Any:
        ancestor = self._ancestor(distance)
        return ancestor.values.get(name)

    def assign_at(self, distance: int, name: Token, value: Any) -> None:
        ancestor = self._ancestor(distance)
        ancestor.values[name.lexeme] = value

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise LoxRuntimeError(name, f"Undefined variable {name.lexeme}.")
