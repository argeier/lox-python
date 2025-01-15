from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar, override

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

    @abstractmethod
    def visit_if_stmt(self, stmt: "If") -> T:
        pass

    @abstractmethod
    def visit_while_stmt(self, stmt: "While") -> T:
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
    def __init__(self, statements: List[Stmt]) -> None:
        self.statements = statements

    @override
    def accept(self, visitor: StmtVisitor[T]) -> None:
        return visitor.visit_block_stmt(self)


class If(Stmt):
    def __init__(
        self, condition: Expr, then_branch: Stmt, else_branch: Stmt | None
    ) -> None:
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    @override
    def accept(self, visitor: StmtVisitor[T]) -> None:
        return visitor.visit_if_stmt(self)


class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt) -> None:
        self.condition = condition
        self.body = body

    @override
    def accept(self, visitor: StmtVisitor[T]) -> None:
        return visitor.visit_while_stmt(self)
