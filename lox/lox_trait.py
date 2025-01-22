from typing import Dict

from .lox_function import LoxFunction
from .tokens import Token


class LoxTrait:
    def __init__(self, name: Token, methods: Dict[str, LoxFunction]):
        self.name: Token = name
        self.methods: Dict[str, LoxFunction] = methods

    def __str__(self):
        return f"<trait {self.name}>"
