from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, override

from .lox_callable import LoxCallable
from .lox_function import LoxFunction
from .lox_instance import LoxInstance

if TYPE_CHECKING:
    from .interpreter import Interpreter


class LoxClass(LoxCallable, LoxInstance):
    """
    Represents a Lox class in the interpreter.

    This class handles the creation and management of Lox classes, including inheritance
    and method lookup. It allows instances to be created and methods to be called
    within the context of the Lox interpreter.

    Attributes:
        name (str): The name of the class.
        superclass (Optional[LoxClass]): The superclass, if any.
        methods (Dict[str, LoxFunction]): The methods defined in the class.
    """

    __slots__ = ("name", "superclass", "methods")

    def __init__(
        self,
        metaclass: Optional[LoxClass],
        name: str,
        superclass: Optional[LoxClass],
        methods: Dict[str, LoxFunction],
    ) -> None:
        super().__init__(metaclass)
        self.name: str = name
        self.superclass: Optional[LoxClass] = superclass
        self.methods: Dict[str, LoxFunction] = methods

    def find_method(self, name: str) -> Optional[LoxFunction]:
        """
        Retrieves a method by name from the class or its superclass.

        Args:
            name (str): The name of the method to find.

        Returns:
            Optional[LoxFunction]: The found method or None if not found.
        """
        if name in self.methods:
            return self.methods.get(name)
        if self.superclass:
            return self.superclass.find_method(name)
        return None

    def __str__(self) -> str:
        """
        Returns the string representation of the clock function.

        Returns:
            str: The string representation.
        """
        return self.name

    @override
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> Any:
        """
        Creates a new instance of the class and initializes it.

        Args:
            interpreter (Interpreter): The interpreter instance.
            arguments (List[Any]): The arguments passed to the constructor.

        Returns:
            Any: The newly created instance.
        """
        instance: LoxInstance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    @override
    def arity(self) -> int:
        """
        Returns the number of parameters the initializer expects.

        Returns:
            int: The arity of the initializer or 0 if none exists.
        """
        initializer = self.find_method("init")
        if initializer:
            return initializer.arity()
        return 0
