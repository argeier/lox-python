from typing import Any, Optional, cast, override

from expr import Binary, Expr, Grouping, Literal, Unary, Visitor
from tokens import Token, TokenType


class LoxRuntimeError(RuntimeError):
    def __init__(self, token: Token, message: str) -> None:
        super().__init__(message)
        self.token = token

    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self) -> str:
        return super().__repr__()


class Interpreter(Visitor[str]):

    def _evaluate(self, expr: Expr | None) -> Any:
        if expr is None:
            self.ast = ""
            return

        return expr.accept(self)

    def _is_truthy(self, obj: Any) -> bool:
        return bool(obj)

    def _is_equal(self, a: Any, b: Any) -> bool:
        return a == b

    def _check_number_operand(self, operator: Token, operand: Any) -> None:
        if isinstance(operand, float):
            return

        raise LoxRuntimeError(operator, "Error: Operand must be [float]")

    def _check_number_operands(self, operator: Token, left: Any, right: Any) -> None:
        if isinstance(left, float) and isinstance(right, float):
            return

        raise LoxRuntimeError(operator, "Error: Operands must be [float,float].")

    def _stringify(self, obj: Any) -> str:
        if obj is None:
            return "null"

        if isinstance(obj, float):
            return str(int(obj)) if obj % 1 == 0 else str(obj)

        return str(obj)

    def interpret(self, expr: Expr | None) -> None:
        try:
            value: Any = self._evaluate(expr)
            print(self._stringify(value))
        except LoxRuntimeError as e:
            print(e)

    @override
    def visit_literal_expr(self, expr: Expr) -> Any:
        assert isinstance(expr, Literal)
        return expr.value

    @override
    def visit_grouping_expr(self, expr: Expr) -> Any:
        assert isinstance(expr, Grouping)
        return self._evaluate(expr.expression)

    @override
    def visit_unary_expr(self, expr: Expr) -> Any:
        assert isinstance(expr, Unary)

        right: Any = self._evaluate(expr.right)

        match (expr.operator.type):
            case TokenType.MINUS:
                self._check_number_operand(expr.operator, right)
                return -right
            case TokenType.BANG:
                return not self._is_truthy(right)
        return None

    @override
    def visit_binary_expr(self, expr: Expr) -> Any:
        assert isinstance(expr, Binary)

        left: Any = self._evaluate(expr.left)
        right: Any = self._evaluate(expr.right)

        match (expr.operator.type):
            case TokenType.MINUS:
                self._check_number_operands(expr.operator, left, right)
                return left - right
            case TokenType.SLASH:
                self._check_number_operands(expr.operator, left, right)
                if int(left) != 0 and int(right) != 0:
                    return left / right
                raise LoxRuntimeError(expr.operator, "Error: division by zero")
            case TokenType.STAR:
                if isinstance(left, float) and isinstance(right, float):
                    return cast(float, left) * cast(float, right)
                elif isinstance(left, str) and isinstance(right, float):
                    return cast(str, left) * int(right)  # TODO:"x"*4.2
                else:
                    raise LoxRuntimeError(
                        expr.operator,
                        "Error: Operands must be [float, float] or [str, float]",
                    )
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return cast(float, left) + cast(float, right)
                elif isinstance(left, str) and isinstance(right, str):
                    return cast(str, left) + cast(str, right)
                elif (isinstance(left, str) and isinstance(right, float)) or (
                    isinstance(left, float) and isinstance(right, str)
                ):
                    return str(left) + str(right)
                else:
                    raise LoxRuntimeError(
                        expr.operator,
                        "Error: Operands must be [str, str] or [float, float]",
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
