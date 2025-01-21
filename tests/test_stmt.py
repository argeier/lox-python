import unittest
from unittest.mock import Mock

from lox.expr import Expr
from lox.stmt import (
    Block,
    Break,
    Expression,
    Function,
    If,
    Print,
    Return,
    StmtVisitor,
    Var,
    While,
)
from lox.tokens import Token, TokenType


class TestStmtVisitor(StmtVisitor[None]):
    def visit_expression_stmt(self, stmt: Expression) -> None:
        pass

    def visit_print_stmt(self, stmt: Print) -> None:
        pass

    def visit_var_stmt(self, stmt: Var) -> None:
        pass

    def visit_block_stmt(self, stmt: Block) -> None:
        pass

    def visit_if_stmt(self, stmt: If) -> None:
        pass

    def visit_while_stmt(self, stmt: While) -> None:
        pass

    def visit_break_stmt(self, stmt: Break) -> None:
        pass

    def visit_function_stmt(self, stmt: Function) -> None:
        pass

    def visit_return_stmt(self, stmt: Return) -> None:
        pass


class TestStmt(unittest.TestCase):
    def setUp(self):
        self.visitor = Mock(spec=TestStmtVisitor)

    def test_expression_stmt(self):
        expr = Mock(spec=Expr)
        stmt = Expression(expr)
        stmt.accept(self.visitor)
        self.visitor.visit_expression_stmt.assert_called_once_with(stmt)

    def test_print_stmt(self):
        expr = Mock(spec=Expr)
        stmt = Print(expr)
        stmt.accept(self.visitor)
        self.visitor.visit_print_stmt.assert_called_once_with(stmt)

    def test_var_stmt(self):
        name = Token(TokenType.IDENTIFIER, "x", None, 1)
        initializer = Mock(spec=Expr)
        stmt = Var(name, initializer)
        stmt.accept(self.visitor)
        self.visitor.visit_var_stmt.assert_called_once_with(stmt)

    def test_block_stmt(self):
        statements = [Mock(spec=Expression)]
        stmt = Block(statements)
        stmt.accept(self.visitor)
        self.visitor.visit_block_stmt.assert_called_once_with(stmt)

    def test_if_stmt(self):
        condition = Mock(spec=Expr)
        then_branch = Mock(spec=Expression)
        else_branch = Mock(spec=Expression)
        stmt = If(condition, then_branch, else_branch)
        stmt.accept(self.visitor)
        self.visitor.visit_if_stmt.assert_called_once_with(stmt)

    def test_while_stmt(self):
        condition = Mock(spec=Expr)
        body = Mock(spec=Expression)
        stmt = While(condition, body)
        stmt.accept(self.visitor)
        self.visitor.visit_while_stmt.assert_called_once_with(stmt)

    def test_break_stmt(self):
        stmt = Break()
        stmt.accept(self.visitor)
        self.visitor.visit_break_stmt.assert_called_once_with(stmt)

    def test_function_stmt(self):
        name = Token(TokenType.IDENTIFIER, "foo", None, 1)
        params = [Token(TokenType.IDENTIFIER, "x", None, 1)]
        body = [Mock(spec=Expression)]
        stmt = Function(name, params, body)
        stmt.accept(self.visitor)
        self.visitor.visit_function_stmt.assert_called_once_with(stmt)

    def test_return_stmt(self):
        keyword = Token(TokenType.RETURN, "return", None, 1)
        value = Mock(spec=Expr)
        stmt = Return(keyword, value)
        stmt.accept(self.visitor)
        self.visitor.visit_return_stmt.assert_called_once_with(stmt)


if __name__ == "__main__":
    unittest.main()
