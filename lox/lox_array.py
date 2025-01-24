from typing import TYPE_CHECKING, Any, List, override

from .callable import LoxCallable
from .error_handler import LoxRuntimeError
from .lox_class import LoxClass
from .lox_instance import LoxInstance
from .tokens import Token

if TYPE_CHECKING:
    from .interpreter import Interpreter


class ArrayGetCallable(LoxCallable):
    def __init__(self, elements: List[Any]):
        self.elements = elements

    @override
    def arity(self) -> int:
        return 1

    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        index: int = int(float(arguments[0]))
        return self.elements[index]

    @override
    def __str__(self) -> str:
        return "<native fn>"


class ArraySetCallable(LoxCallable):
    def __init__(self, elements: List[Any]):
        self.elements = elements

    @override
    def arity(self) -> int:
        return 2

    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        index: int = int(float(arguments[0]))
        value: Any = arguments[1]
        self.elements[index] = value
        return value

    @override
    def __str__(self) -> str:
        return "<native fn>"


class LoxArray(LoxInstance):
    def __init__(self, size: int) -> None:
        array_class: LoxClass = LoxClass(None, "Array", None, {})
        super().__init__(array_class)
        self.elements: List[Any] = [None] * size

    @override
    def get(self, name: Token) -> Any:
        if name.lexeme == "get":
            return ArrayGetCallable(self.elements)
        elif name.lexeme == "set":
            return ArraySetCallable(self.elements)
        elif name.lexeme == "length":
            return float(len(self.elements))

        raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    @override
    def set(self, name: Token, value: Any) -> None:
        raise LoxRuntimeError(name, "Can't add properties to arrays.")

    @override
    def __str__(self) -> str:
        return f"[{', '.join(str(elem) for elem in self.elements)}]"
