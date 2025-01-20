from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar, override

from .expr import Expr
from .tokens import Token

T = TypeVar("T")


class StmtVisitor(ABC, Generic[T]):
    @abstractmethod
    def visit_expression_stmt(self, stmt: "Expression") -> T:
        pass

    @abstractmethod
    def visit_print_stmt(self, stmt: "Print") -> T:
        pass

    @abstractmethod
    def visit_var_stmt(self, stmt: "Var") -> T:
        pass

    @abstractmethod
    def visit_block_stmt(self, stmt: "Block") -> T:
        pass

    @abstractmethod
    def visit_if_stmt(self, stmt: "If") -> T:
        pass

    @abstractmethod
    def visit_while_stmt(self, stmt: "While") -> T:
        pass

    @abstractmethod
    def visit_break_stmt(self, stmt: "Break") -> T:
        pass

    @abstractmethod
    def visit_function_stmt(self, stmt: "Function") -> T:
        pass

    @abstractmethod
    def visit_return_stmt(self, stmt: "Return") -> T:
        pass

    @abstractmethod
    def visit_class_stmt(self, stmt: "Class") -> T:
        pass


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor[T]) -> T:
        pass


class Expression(Stmt):
    def __init__(self, expression: Expr) -> None:
        self.expression: Expr = expression

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_expression_stmt(self)


class Print(Stmt):
    def __init__(self, expression: Expr) -> None:
        self.expression: Expr = expression

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_print_stmt(self)


class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr) -> None:
        self.name: Token = name
        self.initializer: Expr = initializer

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_var_stmt(self)


class Block(Stmt):
    def __init__(self, statements: List[Stmt]) -> None:
        self.statements = statements

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_block_stmt(self)


class Class(Stmt):
    def __init__(self, name: Token, methods: List["Function"]) -> None:
        self.name: Token = name
        self.methods: List["Function"] = methods

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_class_stmt(self)


class Function(Stmt):
    def __init__(self, name: Token, params: List[Token], body: List[Stmt]) -> None:
        self.name: Token = name
        self.params: List[Token] = params
        self.body: List[Stmt] = body

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_function_stmt(self)


class If(Stmt):
    def __init__(
        self, condition: Expr, then_branch: Stmt, else_branch: Stmt | None
    ) -> None:
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_if_stmt(self)


class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt) -> None:
        self.condition = condition
        self.body = body

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_while_stmt(self)


class Break(Stmt):
    def __init__(self) -> None:
        pass

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_break_stmt(self)


class Return(Stmt):
    def __init__(self, keyword: Token, value: Expr | None) -> None:
        self.keyword: Token = keyword
        self.value: Expr | None = value

    @override
    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_return_stmt(self)
