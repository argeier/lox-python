import os
import shutil
from typing import List, Any, Set, Optional, override
from pygraphviz import AGraph
from expr import (
    Binary, Expr, ExprVisitor, Grouping, Literal, Unary, Variable, Assign, Logical, Call,
)
from stmt import (
    Stmt, StmtVisitor, Expression, Print, Var, Block, If, While, Break, Function, Return,
)
from tokens import Token


class AstPrinter(ExprVisitor[str], StmtVisitor[str]):
    """
    AstPrinter generates a visual representation of the Abstract Syntax Tree (AST)
    using pygraphviz. It traverses the AST nodes and creates a corresponding graph image.
    """

    def __init__(self) -> None:
        """
        Initializes the AstPrinter with an empty AST string, a set to track visited nodes,
        and a flag to ensure the AST directory is cleared only once.
        """
        self.ast: str = ""
        self.visited_nodes: Set[str] = set()
        self._ast_directory_cleared: bool = False

    def create_ast(self, statement: Optional[Stmt]) -> None:
        """
        Generates the AST string by visiting the provided statement.

        Args:
            statement (Optional[Stmt]): The root statement of the AST.
        """
        self.ast = statement.accept(self) if statement else ""

    def visualize_ast(self, statement_number: int = 0) -> None:
        """
        Creates a visual representation of the AST and saves it as a PNG image.

        Args:
            statement_number (int): Identifier for the statement, used in the output filename.
        """
        if not self._ast_directory_cleared:
            self._clear_ast_directory()
            self._ast_directory_cleared = True
        graph = AGraph(strict=True, directed=True)
        self._parse_expression(self.ast, graph)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ast_dir = os.path.join(project_root, "assets", "images", "ast")
        os.makedirs(ast_dir, exist_ok=True)
        output_file = os.path.join(ast_dir, f"ast_statement_{statement_number}.png")
        graph.layout(prog="dot")
        graph.draw(output_file)
        print(f"AST image saved to {output_file}")

    def _clear_ast_directory(self) -> None:
        """
        Clears the contents of the AST output directory.
        """
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ast_dir = os.path.join(project_root, "assets", "images", "ast")
        if os.path.exists(ast_dir):
            shutil.rmtree(ast_dir)
        os.makedirs(ast_dir, exist_ok=True)

    def _split_expression(self, expr: str) -> List[str]:
        """
        Splits the parenthesized AST string into individual components.

        Args:
            expr (str): The AST string to split.

        Returns:
            List[str]: A list of split expression parts.
        """
        parts: List[str] = []
        depth: int = 0
        current: str = ""

        for char in expr:
            if char == '(':
                if depth == 0 and current.strip():
                    parts.append(current.strip())
                    current = ""
                depth += 1
                current += char
            elif char == ')':
                depth -= 1
                current += char
                if depth == 0:
                    parts.append(current.strip())
                    current = ""
            elif char == ' ' and depth == 0:
                if current.strip():
                    parts.append(current.strip())
                    current = ""
            else:
                current += char

        if current.strip():
            parts.append(current.strip())

        return parts

    def _parse_expression(
        self,
        expression: str,
        graph: AGraph,
        parent: Optional[str] = None,
        counter: List[int] = [0],
    ) -> None:
        """
        Recursively parses the AST string and constructs the graph.

        Args:
            expression (str): The current expression segment to parse.
            graph (AGraph): The graph being constructed.
            parent (Optional[str]): The parent node ID.
            counter (List[int]): A mutable counter to generate unique node IDs.
        """
        if counter[0] > 1000:
            return

        expression = expression.strip()
        if not expression:
            return

        if expression.startswith("("):
            expr_content = expression[1:-1].strip()
            space_idx = expr_content.find(" ")

            if space_idx == -1:
                operator = expr_content
                remaining = ""
            else:
                operator = expr_content[:space_idx]
                remaining = expr_content[space_idx + 1:]

            node_id = f"node{counter[0]}"
            counter[0] += 1

            if node_id in self.visited_nodes:
                return
            self.visited_nodes.add(node_id)

            graph.add_node(node_id, label=operator)
            if parent:
                graph.add_edge(parent, node_id)

            if remaining:
                child_expressions = self._split_expression(remaining)
                for child_expr in child_expressions:
                    self._parse_expression(child_expr, graph, node_id, counter)
        else:
            node_id = f"node{counter[0]}"
            counter[0] += 1
            graph.add_node(node_id, label=expression)
            if parent:
                graph.add_edge(parent, node_id)

    def _parenthesize(self, name: str, *exprs: Any) -> str:
        """
        Creates a parenthesized string representation of an AST node.

        Args:
            name (str): The name of the AST node.
            *exprs (Any): The child expressions or tokens.

        Returns:
            str: The parenthesized string representation.
        """
        parts: List[str] = [name]
        for expr in exprs:
            if isinstance(expr, (Expr, Stmt)):
                parts.append(str(expr.accept(self)))
            elif isinstance(expr, Token):
                parts.append(expr.lexeme)
            elif isinstance(expr, list):
                parts.extend(str(stmt.accept(self)) for stmt in expr)
            else:
                parts.append(str(expr))
        return f"({' '.join(parts)})"
    @override
    def visit_binary_expr(self, expr: Binary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)
    
    @override
    def visit_call_expr(self, expr: Call) -> str:
        return self._parenthesize("call", expr.callee, *expr.arguments)
    
    @override
    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self._parenthesize("group", expr.expression)
    
    @override
    def visit_literal_expr(self, expr: Literal) -> str:
        return "nil" if expr.value is None else str(expr.value)
    
    @override
    def visit_logical_expr(self, expr: Logical) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    @override
    def visit_unary_expr(self, expr: Unary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.right)

    @override
    def visit_variable_expr(self, expr: Variable) -> str:
        return expr.name.lexeme

    @override
    def visit_assign_expr(self, expr: Assign) -> str:
        return self._parenthesize("=", expr.name, expr.value)

    @override
    def visit_expression_stmt(self, stmt: Expression) -> str:
        return self._parenthesize("expr", stmt.expression)

    @override
    def visit_print_stmt(self, stmt: Print) -> str:
        return self._parenthesize("print", stmt.expression)

    @override
    def visit_var_stmt(self, stmt: Var) -> str:
        return self._parenthesize("var", stmt.name, stmt.initializer) if stmt.initializer else self._parenthesize("var", stmt.name)

    @override
    def visit_block_stmt(self, stmt: Block) -> str:
        return self._parenthesize("block", *stmt.statements)

    @override
    def visit_if_stmt(self, stmt: If) -> str:
        if stmt.else_branch:
            return self._parenthesize("if", stmt.condition, stmt.then_branch, stmt.else_branch)
        return self._parenthesize("if", stmt.condition, stmt.then_branch)

    @override
    def visit_while_stmt(self, stmt: While) -> str:
        return self._parenthesize("while", stmt.condition, stmt.body)

    @override
    def visit_break_stmt(self, stmt: Break) -> str:
        return "(break)"

    @override
    def visit_function_stmt(self, stmt: Function) -> str:
        return self._parenthesize(f"fun {stmt.name.lexeme}", *stmt.body)

    @override
    def visit_return_stmt(self, stmt: Return) -> str:
        return self._parenthesize("return", stmt.value) if stmt.value else "(return)"
