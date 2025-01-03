from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from expr import Expr

# program        → declaration* EOF ;

# declaration    → varDecl
#                | statement ;

# statement      → exprStmt
#                | printStmt ;

T = TypeVar("T")


class StmtVisitor(ABC, Generic[T]):
    @abstractmethod
    def visit_expression_stmt(self, expr: "Expression"):
        pass

    @abstractmethod
    def visit_print_stmt(self, expr: "Print"):
        pass


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor):
        pass


class Expression(Stmt):
    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def accept(self, visitor: StmtVisitor[T]) -> None:
        return visitor.visit_expression_stmt(self)


class Print(Stmt):
    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def accept(self, visitor: StmtVisitor[T]) -> None:
        return visitor.visit_print_stmt(self)
