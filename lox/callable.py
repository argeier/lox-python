from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, List

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
