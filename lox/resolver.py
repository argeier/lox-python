from enum import Enum
from functools import singledispatchmethod
from typing import Dict, Generic, List, TypeVar, override

from .error_handler import ErrorHandler
from .expr import (
    Assign,
    Binary,
    Call,
    Expr,
    ExprVisitor,
    Get,
    Grouping,
    Literal,
    Logical,
    Set,
    This,
    Unary,
    Variable,
)
from .interpreter import Interpreter
from .stmt import (
    Block,
    Break,
    Class,
    Expression,
    Function,
    If,
    Print,
    Return,
    Stmt,
    StmtVisitor,
    Var,
    While,
)
from .tokens import Token

T = TypeVar("T")


class FunctionType(Enum):
    NONE = "NONE"
    FUNCTION = "FUNCTION"
    INITIALIZER = "INITIALIZER"
    METHOD = "METHOD"


class ClassType(Enum):
    NONE = "NONE"
    CLASS = "CLASS"


class Stack(Generic[T]):  # should just use []
    def __init__(self) -> None:
        self._items: List[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def peek(self) -> T:
        if not self._items:
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def __len__(self) -> int:
        return len(self._items)


class Resolver(ExprVisitor[None], StmtVisitor[None]):
    def __init__(self, interpreter: Interpreter, error_handler: ErrorHandler) -> None:
        self._interpreter: Interpreter = interpreter
        self._scopes: Stack[Dict[str, bool]] = Stack()
        self.error_handler: ErrorHandler = error_handler
        self.current_function: FunctionType = FunctionType.NONE
        self.current_class: ClassType = ClassType.NONE

    @override
    def visit_block_stmt(self, stmt: Block) -> None:
        self._begin_scope()
        self.resolve(stmt.statements)
        self._end_scope()
        return None

    @override
    def visit_class_stmt(self, stmt: Class) -> None:
        enclosing_class: ClassType = self.current_class
        self.current_class = ClassType

        self._declare(stmt.name)
        self._define(stmt.name)

        self._begin_scope()
        self._scopes.peek()["this"] = True

        for method in stmt.methods:
            declaration: FunctionType = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self._resolve_function(method, declaration)

        self._end_scope()
        self.current_class = enclosing_class
        return None

    @override
    def visit_expression_stmt(self, stmt: Expression) -> None:
        self.resolve(stmt.expression)
        return None

    @override
    def visit_function_stmt(self, stmt: Function):
        self._declare(stmt.name)
        self._define(stmt.name)
        self._resolve_function(stmt, FunctionType.FUNCTION)
        return None

    @override
    def visit_if_stmt(self, stmt: If) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch:
            self.resolve(stmt.else_branch)
        return None

    @override
    def visit_print_stmt(self, stmt: Print) -> None:
        self.resolve(stmt.expression)
        return None

    @override
    def visit_return_stmt(self, stmt: Return) -> None:
        if self.current_function is FunctionType.NONE:
            self.error_handler.error(stmt.keyword, "Cannot return from top-level code.")
        if stmt.value is not None:
            if self.current_function is FunctionType.INITIALIZER:
                self.error_handler.error(
                    stmt.keyword, "Cannot return a value from an initializer."
                )
            self.resolve(stmt.value)
        return None

    @override
    def visit_while_stmt(self, stmt: While) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.body)
        return None

    @override
    def visit_var_stmt(self, stmt: Var) -> None:
        self._declare(stmt.name)
        if stmt.initializer:
            self.resolve(stmt.initializer)
        self._define(stmt.name)
        return None

    @override
    def visit_break_stmt(self, stmt: "Break") -> None:
        return None

    @override
    def visit_variable_expr(self, expr: Variable) -> None:
        if (
            not self._scopes.is_empty()
            and self._scopes.peek().get(expr.name.lexeme) is False
        ):
            self.error_handler.error(
                expr.name, "Cannot read local variable in its own initializer."
            )
        self._resolve_local(expr, expr.name)
        return None

    @override
    def visit_assign_expr(self, expr: Assign) -> None:
        self.resolve(expr.value)
        self._resolve_local(expr, expr.name)
        return None

    @override
    def visit_binary_expr(self, expr: Binary) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None

    @override
    def visit_call_expr(self, expr: Call) -> None:
        self.resolve(expr.callee)
        for argument in expr.arguments:
            self.resolve(argument)
        return None

    @override
    def visit_get_expr(self, expr: Get) -> None:
        self.resolve(expr.object)
        return None

    @override
    def visit_grouping_expr(self, expr: Grouping) -> None:
        self.resolve(expr.expression)
        return None

    @override
    def visit_literal_expr(self, expr: Literal) -> None:
        return None

    @override
    def visit_logical_expr(self, expr: Logical) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None

    @override
    def visit_set_expr(self, expr: Set) -> None:
        self.resolve(expr.value)
        self.resolve(expr.object)
        return None

    @override
    def visit_this_expr(self, expr: "This") -> None:
        if self.current_class is ClassType.NONE:
            self.error_handler.error(
                expr.keyword, "Cannot use 'this' outside of a class."
            )
            return None
        self._resolve_local(expr, expr.keyword)
        return None

    @override
    def visit_unary_expr(self, expr: Unary) -> None:
        self.resolve(expr.right)
        return None

    @singledispatchmethod
    def resolve(self, obj):
        raise TypeError(f"Unsupported type: {type(obj)}")

    @resolve.register(list)
    def _(self, statements: List[Stmt]):
        for statement in statements:
            self.resolve(statement)

    @resolve.register(Stmt)
    def _(self, stmt: Stmt):
        stmt.accept(self)

    @resolve.register(Expr)
    def _(self, expr: Expr):
        expr.accept(self)

    def _begin_scope(self) -> None:
        scope: Dict[str, bool] = {}
        self._scopes.push(scope)

    def _end_scope(self) -> None:
        self._scopes.pop()

    def _declare(self, name: Token) -> None:
        if self._scopes.is_empty():
            return None
        scope: Dict[str, bool] = self._scopes.peek()
        if scope.get(name.lexeme):
            self.error_handler.error(
                name, "Variable with this name already declared in this scope."
            )
        scope[name.lexeme] = False

    def _define(self, name: Token) -> None:
        if self._scopes.is_empty():
            return None
        scope: Dict[str, bool] = self._scopes.peek()
        scope[name.lexeme] = True

    def _resolve_local(self, expr: Expr, name: Token) -> None:
        for i in range(len(self._scopes) - 1, -1, -1):
            if name.lexeme in self._scopes._items[i]:
                self._interpreter.resolve(expr, len(self._scopes) - 1 - i)
                return None
        return None

    def _resolve_function(self, function: Function, type: FunctionType) -> None:
        enclosing_function: FunctionType = self.current_function
        self.current_function = type
        self._begin_scope()
        for param in function.params:
            self._declare(param)
            self._define(param)
        self.resolve(function.body)
        self._end_scope()
        self.current_function = enclosing_function
        return None
