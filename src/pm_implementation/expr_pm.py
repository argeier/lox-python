from typing import Any


class Expr:
    pass


class Binary(Expr):
    __match_args__ = ("left", "operator", "right")

    def __init__(self, left: Expr, operator: str, right: Expr) -> None:
        self.left = left
        self.operator = operator
        self.right = right


class Grouping(Expr):
    __match_args__ = ("expression",)

    def __init__(self, expression: Expr):
        self.expression = expression


class Literal(Expr):
    __match_args__ = ("value",)

    def __init__(self, value: Any) -> None:
        self.value = value


class Unary(Expr):
    __match_args__ = ("operator", "right")

    def __init__(self, operator: str, right: Expr) -> None:
        self.operator = operator
        self.right = right
