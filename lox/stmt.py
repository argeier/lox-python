from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar, override

from .expr import Expr, Variable
from .tokens import Token

T = TypeVar("T")


class StmtVisitor(ABC, Generic[T]):
    """
    Abstract base class for visiting different types of statements.

    This visitor pattern allows operations to be performed on various
    statement types without modifying their classes.

    Methods:
        visit_expression_stmt (Expression) -> T: Visit an expression statement.
        visit_print_stmt (Print) -> T: Visit a print statement.
        visit_var_stmt (Var) -> T: Visit a variable declaration statement.
        visit_block_stmt (Block) -> T: Visit a block statement.
        visit_if_stmt (If) -> T: Visit an if statement.
        visit_while_stmt (While) -> T: Visit a while statement.
        visit_break_stmt (Break) -> T: Visit a break statement.
        visit_function_stmt (Function) -> T: Visit a function declaration statement.
        visit_return_stmt (Return) -> T: Visit a return statement.
        visit_class_stmt (Class) -> T: Visit a class declaration statement.
        visit_trait_stmt (Trait) -> T: Visit a trait declaration statement.
    """

    @abstractmethod
    def visit_expression_stmt(self, stmt: Expression) -> T: ...

    @abstractmethod
    def visit_print_stmt(self, stmt: Print) -> T: ...

    @abstractmethod
    def visit_var_stmt(self, stmt: Var) -> T: ...

    @abstractmethod
    def visit_block_stmt(self, stmt: Block) -> T: ...

    @abstractmethod
    def visit_if_stmt(self, stmt: If) -> T: ...

    @abstractmethod
    def visit_while_stmt(self, stmt: While) -> T: ...

    @abstractmethod
    def visit_break_stmt(self, stmt: Break) -> T: ...

    @abstractmethod
    def visit_function_stmt(self, stmt: Function) -> T: ...

    @abstractmethod
    def visit_return_stmt(self, stmt: Return) -> T: ...

    @abstractmethod
    def visit_class_stmt(self, stmt: Class) -> T: ...

    @abstractmethod
    def visit_trait_stmt(self, stmt: Trait) -> T: ...


class Stmt(ABC):
    """
    Abstract base class for all statement types.

    Each statement must implement the accept method to allow visitor operations.
    """

    @abstractmethod
    def accept(self, visitor: StmtVisitor[T]) -> T: ...


class Expression(Stmt):
    """
    Represents an expression statement.

    Attributes:
        expression (Expr): The expression to be evaluated.
    """

    __slots__ = ("expression",)

    def __init__(self, expression: Expr) -> None:
        self.expression: Expr = expression

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_expression_stmt(self)


class Print(Stmt):
    """
    Represents a print statement.

    Attributes:
        expression (Expr): The expression to be printed.
    """

    __slots__ = ("expression",)

    def __init__(self, expression: Expr) -> None:
        self.expression: Expr = expression

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_print_stmt(self)


class Var(Stmt):
    """
    Represents a variable declaration statement.

    Attributes:
        name (Token): The name of the variable.
        initializer (Expr): The initializer expression for the variable.
    """

    __slots__ = ("name", "initializer")

    def __init__(self, name: Token, initializer: Expr) -> None:
        self.name: Token = name
        self.initializer: Expr = initializer

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_var_stmt(self)


class Block(Stmt):
    """
    Represents a block of statements.

    Attributes:
        statements (List[Stmt]): The list of statements within the block.
    """

    __slots__ = ("statements",)

    def __init__(self, statements: List[Stmt]) -> None:
        self.statements: List[Stmt] = statements

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_block_stmt(self)


class Class(Stmt):
    """
    Represents a class declaration statement.

    Attributes:
        name (Token): The name of the class.
        superclass (Optional[Variable]): The superclass of the class, if any.
        methods (List[Function]): The list of instance methods.
        class_methods (List[Function]): The list of class methods.
        traits (List[Expr]): The list of traits used by the class.
    """

    __slots__ = ("name", "superclass", "methods", "class_methods", "traits")

    def __init__(
        self,
        name: Token,
        superclass: Optional[Variable],
        methods: List[Function],
        class_methods: List[Function],
        traits: List[Expr],
    ) -> None:
        self.name: Token = name
        self.superclass: Optional[Variable] = superclass
        self.methods: List[Function] = methods
        self.class_methods: List[Function] = class_methods
        self.traits: List[Expr] = traits

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_class_stmt(self)


class Function(Stmt):
    """
    Represents a function declaration statement.

    Attributes:
        name (Token): The name of the function.
        params (Optional[List[Token]]): The list of parameters for the function.
        body (List[Stmt]): The list of statements constituting the function body.
    """

    __slots__ = ("name", "params", "body")

    def __init__(
        self, name: Token, params: Optional[List[Token]], body: List[Stmt]
    ) -> None:
        self.name: Token = name
        self.params: Optional[List[Token]] = params
        self.body: List[Stmt] = body

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_function_stmt(self)


class If(Stmt):
    """
    Represents an if statement.

    Attributes:
        condition (Expr): The condition expression.
        then_branch (Stmt): The statement to execute if the condition is true.
        else_branch (Optional[Stmt]): The statement to execute if the condition is false.
    """

    __slots__ = ("condition", "then_branch", "else_branch")

    def __init__(
        self, condition: Expr, then_branch: Stmt, else_branch: Optional[Stmt]
    ) -> None:
        self.condition: Expr = condition
        self.then_branch: Stmt = then_branch
        self.else_branch: Optional[Stmt] = else_branch

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_if_stmt(self)


class While(Stmt):
    """
    Represents a while loop statement.

    Attributes:
        condition (Expr): The loop condition expression.
        body (Stmt): The body of the loop.
    """

    __slots__ = ("condition", "body")

    def __init__(self, condition: Expr, body: Stmt) -> None:
        self.condition: Expr = condition
        self.body: Stmt = body

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_while_stmt(self)


class Break(Stmt):
    """
    Represents a break statement.
    """

    __slots__ = ()

    def __init__(self) -> None: ...

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_break_stmt(self)


class Return(Stmt):
    """
    Represents a return statement.

    Attributes:
        keyword (Token): The return keyword token.
        value (Optional[Expr]): The expression to return, if any.
    """

    __slots__ = ("keyword", "value")

    def __init__(self, keyword: Token, value: Optional[Expr]) -> None:
        self.keyword: Token = keyword
        self.value: Optional[Expr] = value

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_return_stmt(self)


class Trait(Stmt):
    """
    Represents a trait declaration statement.

    Attributes:
        name (Token): The name of the trait.
        traits (List[Expr]): The list of traits this trait uses.
        methods (List[Function]): The list of methods defined in the trait.
    """

    __slots__ = ("name", "traits", "methods")

    def __init__(
        self, name: Token, traits: List[Expr], methods: List[Function]
    ) -> None:
        self.name: Token = name
        self.traits: List[Expr] = traits
        self.methods: List[Function] = methods

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_trait_stmt(self)
