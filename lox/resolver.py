from __future__ import annotations

from enum import Enum
from functools import singledispatchmethod
from typing import Dict, Generic, List, Optional, TypeVar, override

from .error_handler import ErrorHandler, ParseError
from .expr import (
    Assign,
    Binary,
    Call,
    Conditional,
    Expr,
    ExprVisitor,
    Get,
    Grouping,
    Literal,
    Logical,
    Set,
    Super,
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
    Trait,
    Var,
    While,
)
from .tokens import Token

T = TypeVar("T")


class FunctionType(Enum):
    """
    Enumeration of function types to track the context during resolution.

    Attributes:
        NONE (str): No function context.
        FUNCTION (str): A regular function.
        INITIALIZER (str): An initializer method for a class.
        METHOD (str): An instance method within a class.
    """

    NONE = "NONE"
    FUNCTION = "FUNCTION"
    INITIALIZER = "INITIALIZER"
    METHOD = "METHOD"


class ClassType(Enum):
    """
    Enumeration of class types to track the context during resolution.

    Attributes:
        NONE (str): No class context.
        CLASS (str): A regular class.
        SUBCLASS (str): A subclass inheriting from another class.
        TRAIT (str): A trait within a class.
    """

    NONE = "NONE"
    CLASS = "CLASS"
    SUBCLASS = "SUBCLASS"
    TRAIT = "TRAIT"


class Stack(Generic[T]):
    """
    A simple stack implementation using a list.

    Attributes:
        _items (List[T]): Internal list to store stack items.
    """

    __slots__ = ("_items",)

    def __init__(self) -> None:
        self._items: List[T] = []

    def push(self, item: T) -> None:
        """
        Pushes an item onto the stack.

        Args:
            item (T): The item to push.
        """
        self._items.append(item)

    def pop(self) -> T:
        """
        Pops the top item off the stack.

        Returns:
            T: The popped item.

        Raises:
            IndexError: If the stack is empty.
        """
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def is_empty(self) -> bool:
        """
        Checks if the stack is empty.

        Returns:
            bool: True if the stack is empty, False otherwise.
        """
        return len(self._items) == 0

    def peek(self) -> T:
        """
        Peeks at the top item of the stack without removing it.

        Returns:
            T: The top item.

        Raises:
            IndexError: If the stack is empty.
        """
        if not self._items:
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def __len__(self) -> int:
        """
        Returns the number of items in the stack.

        Returns:
            int: The size of the stack.
        """
        return len(self._items)


class Resolver(ExprVisitor[None], StmtVisitor[None]):
    """
    Resolves variable bindings and scope information for the interpreter.

    This class implements both expression and statement visitors to traverse the
    Abstract Syntax Tree (AST) and determine the scope of each variable and
    resolve variable references.

    Attributes:
        _interpreter (Interpreter): The interpreter instance to communicate resolution.
        _scopes (Stack[Dict[str, bool]]): Stack to manage variable scopes.
        error_handler (ErrorHandler): Handles and reports parsing errors.
        current_function (FunctionType): The current function context.
        current_class (ClassType): The current class context.
    """

    __slots__ = (
        "_interpreter",
        "_scopes",
        "error_handler",
        "current_function",
        "current_class",
    )

    def __init__(self, interpreter: Interpreter, error_handler: ErrorHandler) -> None:
        self._interpreter: Interpreter = interpreter
        self._scopes: Stack[Dict[str, bool]] = Stack()
        self.error_handler: ErrorHandler = error_handler
        self.current_function: FunctionType = FunctionType.NONE
        self.current_class: ClassType = ClassType.NONE

    # Statement Visitors

    @override
    def visit_block_stmt(self, stmt: Block) -> None:
        """
        Visits a block statement, introducing a new scope.

        Args:
            stmt (Block): The block statement to visit.
        """
        self._begin_scope()
        self.resolve(stmt.statements)
        self._end_scope()
        return None

    @override
    def visit_class_stmt(self, stmt: Class) -> None:
        """
        Visits a class declaration, handling superclass and methods.

        Args:
            stmt (Class): The class statement to visit.
        """
        enclosing_class: ClassType = self.current_class
        self.current_class = ClassType.CLASS

        self._declare(stmt.name)
        self._define(stmt.name)

        if stmt.superclass and stmt.name.lexeme == stmt.superclass.name.lexeme:
            self.error_handler.error(
                stmt.superclass.name, "A class can't inherit from itself."
            )

        if stmt.superclass:
            self.current_class = ClassType.SUBCLASS
            self.resolve(stmt.superclass)

        if stmt.superclass:
            self._begin_scope()
            self._scopes.peek()["super"] = True

        self._begin_scope()
        self._scopes.peek()["this"] = True

        for method in stmt.methods:
            declaration: FunctionType = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self._resolve_function(method, declaration)

        for method in stmt.class_methods:
            self._begin_scope()
            self._scopes.peek()["this"] = True
            self._resolve_function(method, FunctionType.METHOD)
            self._end_scope()

        self._end_scope()

        if stmt.superclass:
            self._end_scope()

        self.current_class = enclosing_class
        return None

    @override
    def visit_expression_stmt(self, stmt: Expression) -> None:
        """
        Visits an expression statement and resolves its expression.

        Args:
            stmt (Expression): The expression statement to visit.
        """
        self.resolve(stmt.expression)
        return None

    @override
    def visit_function_stmt(self, stmt: Function) -> None:
        """
        Visits a function declaration, declaring and defining it before resolving its body.

        Args:
            stmt (Function): The function statement to visit.
        """
        self._declare(stmt.name)
        self._define(stmt.name)
        self._resolve_function(stmt, FunctionType.FUNCTION)
        return None

    @override
    def visit_if_stmt(self, stmt: If) -> None:
        """
        Visits an if statement, resolving the condition and branches.

        Args:
            stmt (If): The if statement to visit.
        """
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch:
            self.resolve(stmt.else_branch)
        return None

    @override
    def visit_print_stmt(self, stmt: Print) -> None:
        """
        Visits a print statement and resolves its expression.

        Args:
            stmt (Print): The print statement to visit.
        """
        self.resolve(stmt.expression)
        return None

    @override
    def visit_return_stmt(self, stmt: Return) -> None:
        """
        Visits a return statement, ensuring it is within a function and resolving the return value.

        Args:
            stmt (Return): The return statement to visit.
        """
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
        """
        Visits a while loop statement, resolving its condition and body.

        Args:
            stmt (While): The while statement to visit.
        """
        self.resolve(stmt.condition)
        self.resolve(stmt.body)
        return None

    @override
    def visit_var_stmt(self, stmt: Var) -> None:
        """
        Visits a variable declaration, declaring it before resolving its initializer.

        Args:
            stmt (Var): The variable statement to visit.
        """
        self._declare(stmt.name)
        if stmt.initializer:
            self.resolve(stmt.initializer)
        self._define(stmt.name)
        return None

    @override
    def visit_break_stmt(self, stmt: Break) -> None:
        """
        Visits a break statement. Currently, no action is taken as break handling
        is managed by the interpreter.

        Args:
            stmt (Break): The break statement to visit.
        """
        return None

    @override
    def visit_trait_stmt(self, stmt: Trait) -> None:
        """
        Visits a trait declaration, declaring and defining it before resolving its traits and methods.

        Args:
            stmt (Trait): The trait statement to visit.
        """
        self._declare(stmt.name)
        self._define(stmt.name)
        enclosing_class: ClassType = self.current_class
        self.current_class = ClassType.TRAIT

        for trait in stmt.traits:
            self.resolve(trait)

        self._begin_scope()
        self._scopes.peek()["this"] = True
        for method in stmt.methods:
            declaration: FunctionType = FunctionType.METHOD
            self._resolve_function(method, declaration)
        self._end_scope()
        self.current_class = enclosing_class
        return None

    # Expression Visitors

    @override
    def visit_variable_expr(self, expr: Variable) -> None:
        """
        Visits a variable expression, ensuring it is not used before definition and resolving its scope.

        Args:
            expr (Variable): The variable expression to visit.
        """
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
        """
        Visits an assignment expression, resolving the value and the variable's scope.

        Args:
            expr (Assign): The assignment expression to visit.
        """
        self.resolve(expr.value)
        self._resolve_local(expr, expr.name)
        return None

    @override
    def visit_binary_expr(self, expr: Binary) -> None:
        """
        Visits a binary expression, resolving both operands.

        Args:
            expr (Binary): The binary expression to visit.
        """
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None

    @override
    def visit_call_expr(self, expr: Call) -> None:
        """
        Visits a call expression, resolving the callee and all arguments.

        Args:
            expr (Call): The call expression to visit.
        """
        self.resolve(expr.callee)
        for argument in expr.arguments:
            self.resolve(argument)
        return None

    @override
    def visit_get_expr(self, expr: Get) -> None:
        """
        Visits a get expression, resolving the object from which a property is accessed.

        Args:
            expr (Get): The get expression to visit.
        """
        self.resolve(expr.object)
        return None

    @override
    def visit_grouping_expr(self, expr: Grouping) -> None:
        """
        Visits a grouping expression, resolving the contained expression.

        Args:
            expr (Grouping): The grouping expression to visit.
        """
        self.resolve(expr.expression)
        return None

    @override
    def visit_literal_expr(self, expr: Literal) -> None:
        """
        Visits a literal expression. No action is needed as literals do not require resolution.

        Args:
            expr (Literal): The literal expression to visit.
        """
        return None

    @override
    def visit_logical_expr(self, expr: Logical) -> None:
        """
        Visits a logical expression, resolving both operands.

        Args:
            expr (Logical): The logical expression to visit.
        """
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None

    @override
    def visit_conditional_expr(self, expr: Conditional) -> None:
        """
        Visits a conditional (ternary) expression, resolving the condition and both branches.

        Args:
            expr (Conditional): The conditional expression to visit.
        """
        self.resolve(expr.condition)
        self.resolve(expr.then_branch)
        self.resolve(expr.else_branch)
        return None

    @override
    def visit_set_expr(self, expr: Set) -> None:
        """
        Visits a set expression, resolving the object and the value being assigned.

        Args:
            expr (Set): The set expression to visit.
        """
        self.resolve(expr.value)
        self.resolve(expr.object)
        return None

    @override
    def visit_this_expr(self, expr: This) -> None:
        """
        Visits a 'this' expression, ensuring it is used within a class and resolving its scope.

        Args:
            expr (This): The 'this' expression to visit.
        """
        if self.current_class is ClassType.NONE:
            self.error_handler.error(
                expr.keyword, "Cannot use 'this' outside of a class."
            )
            return None
        self._resolve_local(expr, expr.keyword)
        return None

    @override
    def visit_unary_expr(self, expr: Unary) -> None:
        """
        Visits a unary expression, resolving its operand.

        Args:
            expr (Unary): The unary expression to visit.
        """
        self.resolve(expr.right)
        return None

    @override
    def visit_super_expr(self, expr: Super) -> None:
        """
        Visits a 'super' expression, ensuring it is used within a subclass and resolving its scope.

        Args:
            expr (Super): The 'super' expression to visit.
        """
        if self.current_class is ClassType.NONE:
            self.error_handler.error(
                expr.keyword, "Can't use 'super' outside of a class."
            )
        elif self.current_class is ClassType.TRAIT:
            self.error_handler.error(expr.keyword, "Can't use 'super' in a trait.")
        elif self.current_class is not ClassType.SUBCLASS:
            self.error_handler.error(
                expr.keyword, "Can't use 'super' in a class with no superclass."
            )
        self._resolve_local(expr, expr.keyword)
        return None

    # Utility Methods

    @singledispatchmethod
    def resolve(self, obj):
        """
        Generic resolve method to handle different types of objects.

        Args:
            obj: The object to resolve.

        Raises:
            TypeError: If the object type is unsupported.
        """
        raise TypeError(f"Unsupported type: {type(obj)}")

    @resolve.register(list)
    def _(self, statements: List[Stmt]) -> None:
        """
        Resolves a list of statements.

        Args:
            statements (List[Stmt]): The list of statements to resolve.
        """
        for statement in statements:
            self.resolve(statement)

    @resolve.register(Stmt)
    def _(self, stmt: Stmt) -> None:
        """
        Resolves a single statement by accepting the visitor.

        Args:
            stmt (Stmt): The statement to resolve.
        """
        stmt.accept(self)

    @resolve.register(Expr)
    def _(self, expr: Expr) -> None:
        """
        Resolves a single expression by accepting the visitor.

        Args:
            expr (Expr): The expression to resolve.
        """
        expr.accept(self)

    def _begin_scope(self) -> None:
        """
        Begins a new scope by pushing a new dictionary onto the scope stack.
        """
        scope: Dict[str, bool] = {}
        self._scopes.push(scope)

    def _end_scope(self) -> None:
        """
        Ends the current scope by popping the top dictionary off the scope stack.
        """
        self._scopes.pop()

    def _declare(self, name: Token) -> None:
        """
        Declares a new variable in the current scope without defining it.

        Args:
            name (Token): The name token of the variable to declare.
        """
        if self._scopes.is_empty():
            return None
        scope: Dict[str, bool] = self._scopes.peek()
        if name.lexeme in scope:
            self.error_handler.error(
                name, "Variable with this name already declared in this scope."
            )
        scope[name.lexeme] = False

    def _define(self, name: Token) -> None:
        """
        Defines a variable in the current scope, marking it as initialized.

        Args:
            name (Token): The name token of the variable to define.
        """
        if self._scopes.is_empty():
            return None
        scope: Dict[str, bool] = self._scopes.peek()
        scope[name.lexeme] = True

    def _resolve_local(self, expr: Expr, name: Token) -> None:
        """
        Resolves the scope of a variable and communicates its depth to the interpreter.

        Args:
            expr (Expr): The expression containing the variable.
            name (Token): The name token of the variable.
        """
        for i in range(len(self._scopes) - 1, -1, -1):
            if name.lexeme in self._scopes._items[i]:
                self._interpreter.resolve(expr, len(self._scopes) - 1 - i)
                return None
        # Not found. Assume global.
        return None

    def _resolve_function(self, function: Function, type: FunctionType) -> None:
        """
        Resolves a function's scope and parameters.

        Args:
            function (Function): The function to resolve.
            type (FunctionType): The type of the function being resolved.
        """
        enclosing_function: FunctionType = self.current_function
        self.current_function = type
        self._begin_scope()
        if function.params:
            for param in function.params:
                self._declare(param)
                self._define(param)
        self.resolve(function.body)
        self._end_scope()
        self.current_function = enclosing_function
        return None
