from tmp.expr_pm import Binary, Expr, Grouping, Literal, Unary


class AstPrinter:
    def print(self, expr: Expr) -> str:
        match expr:
            case Binary(left, operator, right):
                return f"({operator} {self.print(left)} {self.print(right)})"
            case Unary(operator, right):
                return f"({operator} {self.print(right)})"
            case Literal(value):
                return "nil" if value is None else str(value)
            case Grouping(expression):
                return f"(group {self.print(expression)})"
            case _:
                raise ValueError("Unknown expression")
