from abc import ABC, abstractmethod
from typing import Generic, TypeVar, override, List

from expr import Expr
from tokens import Token

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


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor) -> T:
        pass


class Expression(Stmt):
    def __init__(self, expression: Expr) -> None:
        self.expression: Expr = expression

    @override
    def accept(self, visitor: StmtVisitor[T]) -> None:
        return visitor.visit_expression_stmt(self)


class Print(Stmt):
    def __init__(self, expression: Expr) -> None:
        self.expression: Expr = expression

    @override
    def accept(self, visitor: StmtVisitor[T]) -> None:
        return visitor.visit_print_stmt(self)


class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr) -> None:
        self.name: Token = name
        self.initializer: Expr = initializer

    @override
    def accept(self, visitor: StmtVisitor[T]) -> None:
        return visitor.visit_var_stmt(self)


class Block(Stmt):
    def __init__(self, statements: List[Stmt]):
        self.statements = statements

    @override
    def accept(self, visitor: StmtVisitor[T]) -> None:
        return visitor.visit_block_stmt(self)
