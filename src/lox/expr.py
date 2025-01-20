from abc import ABC, abstractmethod
from typing import Any, Generic, List, TypeVar, override

from .tokens import Token

T = TypeVar("T")


class ExprVisitor(ABC, Generic[T]):

    @abstractmethod
    def visit_binary_expr(self, expr: "Binary") -> T:
        pass

    @abstractmethod
    def visit_call_expr(self, expr: "Call") -> T:
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

    @abstractmethod
    def visit_variable_expr(self, expr: "Variable") -> T:
        pass

    @abstractmethod
    def visit_assign_expr(self, expr: "Assign") -> T:
        pass

    @abstractmethod
    def visit_logical_expr(self, expr: "Logical") -> T:
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

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_binary_expr(self)


class Call(Expr):
    def __init__(self, callee: Expr, paren: Token, arguments: List[Expr]) -> None:
        self.callee: Expr = callee
        self.paren: Token = paren
        self.arguments: List[Expr] = arguments

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_call_expr(self)


class Grouping(Expr):

    def __init__(self, expression: Expr) -> None:
        self.expression: Expr = expression

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_grouping_expr(self)


class Literal(Expr):

    def __init__(self, value: Any) -> None:
        self.value: Any = value

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_literal_expr(self)


class Unary(Expr):

    def __init__(self, operator: Token, right: Expr) -> None:
        self.operator: Token = operator
        self.right: Expr = right

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_unary_expr(self)


class Variable(Expr):

    def __init__(self, name: Token) -> None:
        self.name: Token = name

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_variable_expr(self)


class Assign(Expr):
    def __init__(self, name: Token, value: Expr) -> None:
        self.name = name
        self.value = value

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_assign_expr(self)


class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_logical_expr(self)
