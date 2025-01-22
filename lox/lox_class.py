from typing import TYPE_CHECKING, Any, Dict, List, override

if TYPE_CHECKING:
    from .interpreter import Interpreter

from .lox_callable import LoxCallable
from .lox_function import LoxFunction
from .lox_instance import LoxInstance


class LoxClass(LoxCallable, LoxInstance):
    def __init__(
        self,
        metaclass: "LoxClass",
        name: str,
        superclass: "LoxClass",
        methods: Dict[str, LoxFunction],
    ) -> None:
        super().__init__(metaclass)
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def find_method(self, name: str) -> LoxCallable | None:
        if name in self.methods:
            return self.methods.get(name)
        if self.superclass:
            return self.superclass.find_method(name)
        return None

    def __str__(self) -> str:
        return self.name

    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        instance: "LoxInstance" = LoxInstance(self)
        if initializer := self.find_method("init"):
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    @override
    def arity(self) -> int:
        if initializer := self.find_method("init"):
            return initializer.arity()
        return 0
