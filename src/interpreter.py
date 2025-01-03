from typing import Any, List, cast, override

from expr import Binary, Expr, ExprVisitor, Grouping, Literal, Unary
from stmt import Expression, Print, Stmt, StmtVisitor
from tokens import Token, TokenType


class LoxRuntimeError(RuntimeError):

    def __init__(self, token: Token, message: str) -> None:

        super().__init__(message)
        self.token = token

    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self) -> str:
        return super().__repr__()


class Interpreter(ExprVisitor[Any], StmtVisitor[None]):

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
            return "null"
        if isinstance(obj, float):
            return str(int(obj)) if obj % 1 == 0 else str(obj)
        return str(obj)

    def _execute(self, stmt: Stmt) -> None:
        stmt.accept(self)

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
    def visit_expression_stmt(self, stmt: Expression) -> None:
        self._evaluate(stmt.expression)

    @override
    def visit_print_stmt(self, stmt: Print) -> None:
        value: Any = self._evaluate(stmt.expression)
        print(self._stringify(value))
