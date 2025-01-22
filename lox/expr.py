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

    @abstractmethod
    def visit_get_expr(self, expr: "Get") -> T:
        pass

    @abstractmethod
    def visit_set_expr(self, expr: "Set") -> T:
        pass

    @abstractmethod
    def visit_this_expr(self, expr: "This") -> T:
        pass

    @abstractmethod
    def visit_super_expr(self, expr: "Super") -> T:
        pass

    @abstractmethod
    def visit_conditional_expr(self, expr: "Conditional") -> T:
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


class Get(Expr):
    def __init__(self, object: Expr, name: Token) -> None:
        self.object = object
        self.name = name

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_get_expr(self)


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


class Set(Expr):
    def __init__(self, object: Expr, name: Token, value: Expr) -> None:
        self.object = object
        self.name = name
        self.value = value

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_set_expr(self)


class Super(Expr):
    def __init__(self, keyword: Token, method: Token) -> None:
        self.keyword = keyword
        self.method = method

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_super_expr(self)


class This(Expr):
    def __init__(self, keyword: Token) -> None:
        self.keyword = keyword

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_this_expr(self)


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


class Conditional(Expr):
    def __init__(self, condition: Expr, then_branch: Expr, else_branch: Expr) -> None:
        self.condition: Expr = condition
        self.then_branch: Expr = then_branch
        self.else_branch: Expr = else_branch

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_conditional_expr(self)
