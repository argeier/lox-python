import unittest
from pathlib import Path
from unittest.mock import patch

from lox.ast_printer import AstPrinter
from lox.expr import Binary, Literal, Variable
from lox.stmt import Expression, Print, Var
from lox.tokens import Token, TokenType


class TestAstPrinter(unittest.TestCase):
    def setUp(self):
        self.ast_printer = AstPrinter()
        self.ast_printer._output_dir = Path("test_output")
        self.token = lambda type, lexeme: Token(type, lexeme, None, 1)

    def test_split_expression(self):
        expressions = [
            ("(+ 1 2)", ["(+ 1 2)"]),
            ('print "hello"', ["print", '"hello"']),
            ("(group (+ 1 2))", ["(group (+ 1 2))"]),
            ('(print "hello" "world")', ['(print "hello" "world")']),
        ]

        for expr, expected in expressions:
            with self.subTest(expr=expr):
                result = self.ast_printer._split_expression(expr)
                self.assertEqual(result, expected)

    def test_parse_literal_expr(self):
        with patch("pygraphviz.AGraph") as MockAGraph:
            mock_graph = MockAGraph()
            self.ast_printer._parse_literal_expr("42", mock_graph)
            mock_graph.add_node.assert_called_once()
            args = mock_graph.add_node.call_args[0]
            self.assertTrue(args[0].startswith("node"))
            self.assertEqual(mock_graph.add_node.call_args[1]["label"], "Number: 42")

    def test_basic_expressions(self):
        expr = Binary(Literal(1), self.token(TokenType.PLUS, "+"), Literal(2))
        result = expr.accept(self.ast_printer)
        self.assertEqual(result, "(+ 1 2)")

    def test_nested_expressions(self):
        inner = Binary(Literal(2), self.token(TokenType.STAR, "*"), Literal(3))
        outer = Binary(inner, self.token(TokenType.PLUS, "+"), Literal(1))
        result = outer.accept(self.ast_printer)
        self.assertEqual(result, "(+ (* 2 3) 1)")

    def test_variable_declaration(self):
        var_stmt = Var(self.token(TokenType.IDENTIFIER, "x"), Literal(42))
        result = var_stmt.accept(self.ast_printer)
        self.assertEqual(result, "(var x 42)")

    def test_print_statement(self):
        print_stmt = Print(Literal("hello"))
        result = print_stmt.accept(self.ast_printer)
        self.assertEqual(result, '(print "hello")')

    def test_create_ast(self):
        stmt = Print(Literal(42))
        self.ast_printer.create_ast(stmt)
        self.assertEqual(self.ast_printer.ast, "(print 42)")

        self.ast_printer.create_ast(None)
        self.assertEqual(self.ast_printer.ast, "")

    def test_expression_parsing(self):
        expr = "(+ 1 (* 2 3))"
        with patch("pygraphviz.AGraph") as MockAGraph:
            mock_graph = MockAGraph()
            self.ast_printer._parse_expression(expr, mock_graph)
            # Verify nodes were added for operators and numbers
            self.assertGreater(mock_graph.add_node.call_count, 3)

    def test_variable_expr(self):
        var = Variable(self.token(TokenType.IDENTIFIER, "foo"))
        result = var.accept(self.ast_printer)
        self.assertEqual(result, "foo")

    def test_expression_stmt(self):
        expr_stmt = Expression(Literal(42))
        result = expr_stmt.accept(self.ast_printer)
        self.assertEqual(result, "(expr 42)")


if __name__ == "__main__":
    unittest.main()
