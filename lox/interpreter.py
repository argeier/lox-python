from typing import Any, Dict, Final, List, cast, override

from .environment import Environment
from .error_handler import BreakException, LoxRuntimeError, ReturnException
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
    Super,
    This,
    Unary,
    Variable,
)
from .lox_callable import ClockCallable, LoxCallable
from .lox_class import LoxClass
from .lox_function import LoxFunction
from .lox_instance import LoxInstance
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
from .tokens import Token, TokenType


class Interpreter(ExprVisitor[Any], StmtVisitor[None]):

    def __init__(self) -> None:
        self.globals: Final[Environment] = Environment()
        self._environment: Environment = self.globals
        self._locals: Dict[Expr, int] = {}

        self.globals.define("clock", ClockCallable())

    def _evaluate(self, expr: Expr | None) -> Any:
        if expr is None:
            return None

        return expr.accept(self)

    def _is_truthy(self, obj: Any) -> bool:
        return bool(obj)

    def _is_equal(self, a: Any, b: Any) -> bool:
        return a == b

    def _check_number_operand(self, operator: Token, operand: Any) -> None:
        if not isinstance(operand, float):
            raise LoxRuntimeError(operator, "Operand must be a number.")

    def _check_number_operands(self, operator: Token, left: Any, right: Any) -> None:
        if not (isinstance(left, float) and isinstance(right, float)):
            raise LoxRuntimeError(operator, "Operands must be numbers.")

    def _stringify(self, obj: Any) -> str:
        if obj is None:
            raise LoxRuntimeError(
                Token(TokenType.NIL, "nil", None, 0),  # Create a dummy token
                "Error: Variable access before initialization or assignment",
            )
            # return "null" # implicit initializiation as null
        if isinstance(obj, float):
            return str(int(obj)) if obj % 1 == 0 else str(obj)
        return str(obj)

    def _execute(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def resolve(self, expr: Expr, depth: int) -> None:
        self._locals[expr] = depth

    def _execute_block(self, statements: List[Stmt], environment: Environment) -> None:
        previous: Environment = self._environment

        try:
            self._environment = environment
            for statement in statements:
                self._execute(statement)
        finally:
            self._environment = previous

    def interpret(self, statements: List[Stmt]) -> None:
        try:
            for statement in statements:
                self._execute(statement)
        except LoxRuntimeError as e:
            print(e)

    @override
    def visit_literal_expr(self, expr: Literal) -> Any:
        return expr.value

    @override
    def visit_grouping_expr(self, expr: Grouping) -> Any:
        return self._evaluate(expr.expression)

    @override
    def visit_unary_expr(self, expr: Unary) -> Any:
        right: Any = self._evaluate(expr.right)

        match expr.operator.type:
            case TokenType.MINUS:
                self._check_number_operand(expr.operator, right)
                return -right
            case TokenType.BANG:
                return not self._is_truthy(right)
        return None

    @override
    def visit_binary_expr(self, expr: Binary) -> Any:
        left: Any = self._evaluate(expr.left)
        right: Any = self._evaluate(expr.right)

        match expr.operator.type:
            case TokenType.MINUS:
                self._check_number_operands(expr.operator, left, right)
                return left - right
            case TokenType.SLASH:
                self._check_number_operands(expr.operator, left, right)
                if right == 0:
                    raise LoxRuntimeError(expr.operator, "Division by zero.")
                return left / right
            case TokenType.STAR:
                if isinstance(left, float) and isinstance(right, float):
                    return cast(float, left) * cast(float, right)
                elif isinstance(left, str) and isinstance(right, float):
                    return cast(str, left) * int(right)
                raise LoxRuntimeError(
                    expr.operator, "Operands must be numbers or a string and a number."
                )
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return cast(float, left) + cast(float, right)
                elif isinstance(left, str) and isinstance(right, str):
                    return cast(str, left) + cast(str, right)
                raise LoxRuntimeError(
                    expr.operator, "Operands must be two numbers or two strings."
                )
            case TokenType.GREATER:
                self._check_number_operands(expr.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                self._check_number_operands(expr.operator, left, right)
                return left >= right
            case TokenType.LESS:
                self._check_number_operands(expr.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                self._check_number_operands(expr.operator, left, right)
                return left <= right
            case TokenType.BANG_EQUAL:
                return not self._is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self._is_equal(left, right)

    @override
    def visit_variable_expr(self, expr: "Variable") -> Any:
        return self._lookup_variable(expr.name, expr)

    def _lookup_variable(self, name: Token, expr: Variable) -> Any:
        distance: int = self._locals.get(expr, -1)
        if distance != -1:
            return self._environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

    @override
    def visit_assign_expr(self, expr: "Assign") -> Any:
        value: Any = self._evaluate(expr.value)

        distance: int = self._locals.get(expr, -1)
        if distance != -1:
            self._environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)

        return value

    @override
    def visit_logical_expr(self, expr: "Logical") -> Any:
        left: Any = self._evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if self._is_truthy(left):
                return left
        else:
            if not self._is_truthy(left):
                return left

        return self._evaluate(expr.right)

    @override
    def visit_set_expr(self, expr: "Set") -> Any:
        obj: Any = self._evaluate(expr.object)

        if not isinstance(obj, LoxInstance):
            raise LoxRuntimeError(expr.name, "Only instances have fields.")

        value: Any = self._evaluate(expr.value)
        obj.set(expr.name, value)
        return value

    @override
    def visit_super_expr(self, expr: "Super") -> Any:
        distance: int = self._locals[expr]
        superclass: LoxClass = self._environment.get_at(distance, "super")
        obj: LoxInstance = self._environment.get_at(distance - 1, "this")
        method: LoxFunction = superclass.find_method(expr.method.lexeme)
        if method is None:
            raise RuntimeError(
                expr.method, f"Undefined property '{expr.method.lexeme}.'"
            )
        return method.bind(obj)

    @override
    def visit_this_expr(self, expr: "This") -> Any:
        return self._lookup_variable(expr.keyword, expr)

    @override
    def visit_call_expr(self, expr: "Call") -> Any:
        callee: Any = self._evaluate(expr.callee)

        arguements: List[Any] = [
            self._evaluate(arguement) for arguement in expr.arguments
        ]

        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")

        function: LoxCallable = cast(LoxCallable, callee)

        if len(arguements) != function.arity():
            raise LoxRuntimeError(
                expr.paren,
                f"Expected {function.arity()} arguments but got {len(arguements)}.",
            )

        return function.call(self, arguements)

    @override
    def visit_get_expr(self, expr: Get) -> Any:
        obj: Any = self._evaluate(expr.object)
        if isinstance(obj, LoxInstance):
            result = obj.get(expr.name)
            if isinstance(result, LoxFunction) and result.is_getter():
                return result.call(self, [])
            return obj.get(expr.name)

        raise LoxRuntimeError(expr.name, "Only instances have properties.")

    @override
    def visit_expression_stmt(self, stmt: Expression) -> None:
        self._evaluate(stmt.expression)

    @override
    def visit_print_stmt(self, stmt: Print) -> None:
        value: Any = self._evaluate(stmt.expression)
        print(self._stringify(value))

    @override
    def visit_var_stmt(self, stmt: "Var") -> None:
        value: Any = None
        if stmt.initializer is not None:
            value = self._evaluate(stmt.initializer)

        self._environment.define(stmt.name.lexeme, value)
        return None

    @override
    def visit_block_stmt(self, stmt: "Block") -> None:
        self._execute_block(stmt.statements, Environment(self._environment))
        return None

    @override
    def visit_class_stmt(self, stmt: Class) -> None:
        superclass: Any = None
        if stmt.superclass:
            superclass = self._evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise RuntimeError(stmt.superclass.name, "Superclass must be a class.")

        self._environment.define(stmt.name.lexeme, None)

        if stmt.superclass:
            self._environment = Environment(self._environment)
            self._environment.define("super", superclass)

        class_methods: Dict[str, LoxFunction] = {
            method.name.lexeme: LoxFunction(method, self._environment, False)
            for method in stmt.class_methods
        }

        metaclass: LoxClass = LoxClass(
            None, stmt.name.lexeme + " metaclass", superclass, class_methods
        )

        methods: Dict[str, LoxFunction] = {
            method.name.lexeme: LoxFunction(
                method, self._environment, method.name.lexeme == "init"
            )
            for method in stmt.methods
        }

        klass: LoxClass = LoxClass(metaclass, stmt.name.lexeme, superclass, methods)

        if superclass:
            self._environment = self._environment.enclosing

        self._environment.assign(stmt.name, klass)
        return None

    @override
    def visit_if_stmt(self, stmt: "If") -> None:
        if self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self._execute(stmt.else_branch)
        return None

    @override
    def visit_while_stmt(self, stmt: "While") -> None:
        while self._is_truthy(self._evaluate(stmt.condition)):
            try:
                self._execute(stmt.body)
            except BreakException:
                break
        return None

    @override
    def visit_break_stmt(self, stmt: "Break") -> None:
        raise BreakException()

    @override
    def visit_function_stmt(self, stmt: Function) -> None:
        from .lox_function import LoxFunction  # to avoid circular import

        function: LoxFunction = LoxFunction(stmt, self._environment, False)
        self._environment.define(stmt.name.lexeme, function)
        return None

    @override
    def visit_return_stmt(self, stmt: "Return"):
        value: Any = None
        if stmt.value is not None:
            value = self._evaluate(stmt.value)

        raise ReturnException(value)
