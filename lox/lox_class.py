from typing import TYPE_CHECKING, Any, Dict, List, override

if TYPE_CHECKING:
    from .interpreter import Interpreter

from .lox_callable import LoxCallable
from .lox_function import LoxFunction
from .lox_instance import LoxInstance
from .tokens import Token


class LoxClass(LoxCallable, LoxInstance):
    def __init__(self, name: str, methods: Dict[str, LoxFunction]) -> None:
        self.name = name
        self.instance_methods = {}
        self.class_methods = {}

        for method_name, method in methods.items():
            if method.is_class_method:
                self.class_methods[method_name] = method.bind(self)
            else:
                self.instance_methods[method_name] = method

        super().__init__(self)

    def find_method(self, name: str) -> LoxCallable:
        return self.instance_methods.get(name)

    def find_class_method(self, name: str) -> LoxCallable:
        return self.class_methods.get(name)

    def __str__(self) -> str:
        return self.name

    @override
    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        instance: LoxInstance = LoxInstance(self)
        if initializer := self.find_method("init"):
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    @override
    def arity(self) -> int:
        if initializer := self.find_method("init"):
            return initializer.arity()
        return 0

    @override
    def get(self, name: Token) -> Any:
        if (method := self.find_class_method(name.lexeme)) is not None:
            return method
        return super().get(name)
