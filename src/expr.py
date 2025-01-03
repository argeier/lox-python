from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from tokens import Token

T = TypeVar("T")


class ExprVisitor(ABC, Generic[T]):

    @abstractmethod
    def visit_binary_expr(self, expr: "Binary") -> T:
        pass

    @abstractmethod
    def visit_grouping_expr(self, expr: "Grouping") -> T:
        pass

    @abstractmethod
    def visit_literal_expr(self, expr: "Literal") -> T:
        pass

    @abstractmethod
    def visit_unary_expr(self, expr: "Unary") -> T:
        pass


class Expr(ABC):

    @abstractmethod
    def accept(self, visitor: ExprVisitor[T]) -> T:
        pass


class Binary(Expr):

    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left: Expr = left
        self.operator: Token = operator
        self.right: Expr = right

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_binary_expr(self)


class Grouping(Expr):

    def __init__(self, expression: Expr) -> None:
        self.expression: Expr = expression

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_grouping_expr(self)


class Literal(Expr):

    def __init__(self, value: Any) -> None:
        self.value: Any = value

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_literal_expr(self)


class Unary(Expr):

    def __init__(self, operator: Token, right: Expr) -> None:
        self.operator: Token = operator
        self.right: Expr = right

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_unary_expr(self)
