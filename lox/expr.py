from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar, override

from .tokens import Token

T = TypeVar("T")


class ExprVisitor(ABC, Generic[T]):
    """
    Visitor interface for processing different types of expressions in the AST.

    This interface defines a visit method for each concrete expression type,
    allowing operations to be performed on expressions by implementing the visitor.

    Methods:
        visit_binary_expr (Binary) -> T: Visit a Binary expression.
        visit_call_expr (Call) -> T: Visit a Call expression.
        visit_grouping_expr (Grouping) -> T: Visit a Grouping expression.
        visit_literal_expr (Literal) -> T: Visit a Literal expression.
        visit_unary_expr (Unary) -> T: Visit a Unary expression.
        visit_variable_expr (Variable) -> T: Visit a Variable expression.
        visit_assign_expr (Assign) -> T: Visit an Assign expression.
        visit_logical_expr (Logical) -> T: Visit a Logical expression.
        visit_get_expr (Get) -> T: Visit a Get expression.
        visit_set_expr (Set) -> T: Visit a Set expression.
        visit_this_expr (This) -> T: Visit a This expression.
        visit_super_expr (Super) -> T: Visit a Super expression.
        visit_conditional_expr (Conditional) -> T: Visit a Conditional expression.
    """

    @abstractmethod
    def visit_binary_expr(self, expr: Binary) -> T: ...

    @abstractmethod
    def visit_call_expr(self, expr: Call) -> T: ...

    @abstractmethod
    def visit_grouping_expr(self, expr: Grouping) -> T: ...

    @abstractmethod
    def visit_literal_expr(self, expr: Literal) -> T: ...

    @abstractmethod
    def visit_unary_expr(self, expr: Unary) -> T: ...

    @abstractmethod
    def visit_variable_expr(self, expr: Variable) -> T: ...

    @abstractmethod
    def visit_assign_expr(self, expr: Assign) -> T: ...

    @abstractmethod
    def visit_logical_expr(self, expr: Logical) -> T: ...

    @abstractmethod
    def visit_get_expr(self, expr: Get) -> T: ...

    @abstractmethod
    def visit_set_expr(self, expr: Set) -> T: ...

    @abstractmethod
    def visit_this_expr(self, expr: This) -> T: ...

    @abstractmethod
    def visit_super_expr(self, expr: Super) -> T: ...

    @abstractmethod
    def visit_conditional_expr(self, expr: Conditional) -> T: ...


class Expr(ABC):
    """
    Abstract base class for all expression nodes in the AST.

    This class defines the interface for expression nodes, requiring the
    implementation of the accept method to accept visitors.
    """

    @abstractmethod
    def accept(self, visitor: ExprVisitor[T]) -> T: ...


class Binary(Expr):
    """
    Represents a binary operation expression.

    Attributes:
        left (Expr): The left operand.
        operator (Token): The operator token.
        right (Expr): The right operand.
    """

    __slots__ = ("left", "operator", "right")

    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left: Expr = left
        self.operator: Token = operator
        self.right: Expr = right

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_binary_expr(self)


class Call(Expr):
    """
    Represents a function or method call expression.

    Attributes:
        callee (Expr): The expression being called.
        paren (Token): The closing parenthesis token.
        arguments (List[Expr]): The list of argument expressions.
    """

    __slots__ = ("callee", "paren", "arguments")

    def __init__(self, callee: Expr, paren: Token, arguments: List[Expr]) -> None:
        self.callee: Expr = callee
        self.paren: Token = paren
        self.arguments: List[Expr] = arguments

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_call_expr(self)


class Get(Expr):
    """
    Represents a property access expression.

    Attributes:
        object (Expr): The object whose property is being accessed.
        name (Token): The name of the property.
    """

    __slots__ = ("object", "name")

    def __init__(self, object: Expr, name: Token) -> None:
        self.object: Expr = object
        self.name: Token = name

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_get_expr(self)


class Grouping(Expr):
    """
    Represents a grouping of expressions, typically using parentheses.

    Attributes:
        expression (Expr): The grouped expression.
    """

    __slots__ = ("expression",)

    def __init__(self, expression: Expr) -> None:
        self.expression: Expr = expression

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_grouping_expr(self)


class Literal(Expr):
    """
    Represents a literal value expression.

    Attributes:
        value (Any): The literal value.
    """

    __slots__ = ("value",)

    def __init__(self, value: Any) -> None:
        self.value: Any = value

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_literal_expr(self)


class Set(Expr):
    """
    Represents a property assignment expression.

    Attributes:
        object (Expr): The object whose property is being assigned.
        name (Token): The name of the property.
        value (Expr): The value being assigned to the property.
    """

    __slots__ = ("object", "name", "value")

    def __init__(self, object: Expr, name: Token, value: Expr) -> None:
        self.object: Expr = object
        self.name: Token = name
        self.value: Expr = value

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_set_expr(self)


class Super(Expr):
    """
    Represents a 'super' keyword expression, used to access superclass methods.

    Attributes:
        keyword (Token): The 'super' keyword token.
        method (Token): The method name token.
    """

    __slots__ = ("keyword", "method")

    def __init__(self, keyword: Token, method: Token) -> None:
        self.keyword: Token = keyword
        self.method: Token = method

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_super_expr(self)


class This(Expr):
    """
    Represents a 'this' keyword expression, referring to the current instance.

    Attributes:
        keyword (Token): The 'this' keyword token.
    """

    __slots__ = ("keyword",)

    def __init__(self, keyword: Token) -> None:
        self.keyword: Token = keyword

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_this_expr(self)


class Unary(Expr):
    """
    Represents a unary operation expression.

    Attributes:
        operator (Token): The operator token.
        right (Expr): The operand expression.
    """

    __slots__ = ("operator", "right")

    def __init__(self, operator: Token, right: Expr) -> None:
        self.operator: Token = operator
        self.right: Expr = right

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_unary_expr(self)


class Variable(Expr):
    """
    Represents a variable expression.

    Attributes:
        name (Token): The variable name token.
    """

    __slots__ = ("name",)

    def __init__(self, name: Token) -> None:
        self.name: Token = name

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_variable_expr(self)


class Assign(Expr):
    """
    Represents an assignment expression.

    Attributes:
        name (Token): The variable name token.
        value (Expr): The expression representing the value to assign.
    """

    __slots__ = ("name", "value")

    def __init__(self, name: Token, value: Expr) -> None:
        self.name: Token = name
        self.value: Expr = value

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_assign_expr(self)


class Logical(Expr):
    """
    Represents a logical operation expression (e.g., and, or).

    Attributes:
        left (Expr): The left operand expression.
        operator (Token): The operator token.
        right (Expr): The right operand expression.
    """

    __slots__ = ("left", "operator", "right")

    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left: Expr = left
        self.operator: Token = operator
        self.right: Expr = right

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_logical_expr(self)


class Conditional(Expr):
    """
    Represents a conditional (ternary) expression.

    Attributes:
        condition (Expr): The condition expression.
        then_branch (Expr): The expression to evaluate if the condition is true.
        else_branch (Expr): The expression to evaluate if the condition is false.
    """

    __slots__ = ("condition", "then_branch", "else_branch")

    def __init__(self, condition: Expr, then_branch: Expr, else_branch: Expr) -> None:
        self.condition: Expr = condition
        self.then_branch: Expr = then_branch
        self.else_branch: Expr = else_branch

    @override
    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_conditional_expr(self)
