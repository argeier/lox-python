from typing import Dict, List, override, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .interpreter import Interpreter

from .lox_callable import LoxCallable
from .lox_instance import LoxInstance
from .lox_function import LoxFunction


class LoxClass(LoxCallable):
    def __init__(self, name: str, methods: Dict[str, LoxFunction]) -> None:
        self.name = name
        self.methods = methods

    def find_method(self, name: str) -> LoxCallable:
        return self.methods.get(name)

    def __str__(self) -> str:
        return self.name

    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        instance: "LoxInstance" = LoxInstance(self)
        return instance

    @override
    def arity(self) -> int:
        return 0
