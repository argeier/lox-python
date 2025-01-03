from dataclasses import dataclass
from typing import Any


class Expr:
    pass


@dataclass
class Binary(Expr):
    __match_args__ = ("left", "operator", "right")
    left: Expr
    operator: str
    right: Expr


@dataclass
class Unary(Expr):
    __match_args__ = ("operator", "right")
    operator: str
    right: Expr


@dataclass
class Literal(Expr):
    __match_args__ = ("value",)
    value: Any


@dataclass
class Grouping(Expr):
    __match_args__ = ("expression",)
    expression: Expr
