from abc import ABC, abstractmethod
from time import time
from typing import TYPE_CHECKING, Any, List, override

if TYPE_CHECKING:
    from .interpreter import Interpreter


class LoxCallable(ABC):

    @abstractmethod
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        pass

    @abstractmethod
    def arity(self) -> int:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


class ClockCallable(LoxCallable):

    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        return time()

    @override
    def arity(self) -> int:
        return 0

    @override
    def __str__(self) -> str:
        return "<native fn>"
