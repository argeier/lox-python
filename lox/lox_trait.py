from __future__ import annotations

from typing import Dict

from .lox_function import LoxFunction
from .tokens import Token


class LoxTrait:
    """
    Represents a trait in the Lox language.

    This class encapsulates a trait's name and its associated methods.
    Traits provide a way to define reusable method collections that can be
    included in classes, promoting code reuse and modularity.

    Attributes:
        name (Token): The name of the trait.
        methods (Dict[str, LoxFunction]): A dictionary mapping method names to their corresponding LoxFunction implementations.
    """

    __slots__ = ("name", "methods")

    def __init__(self, name: Token, methods: Dict[str, LoxFunction]) -> None:
        self.name: Token = name
        self.methods: Dict[str, LoxFunction] = methods

    def __str__(self) -> str:
        return f"<trait {self.name}>"
