from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional
from typing import Set as PySet
from typing import TypeVar

from pygraphviz import AGraph

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
)
from .expr import Set as ExprSet  # Renamed to avoid conflict with built-in set
from .expr import Super, This, Unary, Variable
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


@dataclass
class GraphNode:
    """
    Represents a node in the Abstract Syntax Tree visualization graph.

    Attributes:
        id (str): Unique identifier for the node.
        label (str): Display label for the node.
        parent (Optional[str]): ID of the parent node, if any.
    """

    id: str
    label: str
    parent: Optional[str] = None


class AstPrinter(ExprVisitor[str], StmtVisitor[str]):
    """
    AST visualization generator implementing both expression and statement visitors.

    This class traverses the Abstract Syntax Tree (AST) to generate both string
    representations and visual graph outputs. It implements the Visitor pattern through
    both ExprVisitor and StmtVisitor interfaces to handle all types of AST nodes.

    Attributes:
        _ast (str): Current AST string representation.
        _visited_nodes (PySet[str]): Set of processed node IDs.
        _ast_directory_cleared (bool): Flag indicating if output directory is cleared.
        _node_counter (int): Counter for generating unique node IDs.
        _output_dir (Path): Directory path for saving visualization outputs.
    """

    def __init__(self) -> None:
        """
        Initialize the AST printer with empty state for visualization generation.
        """
        self._ast: str = ""
        self._visited_nodes: PySet[str] = set()
        self._ast_directory_cleared: bool = False
        self._node_counter: int = 0
        self._output_dir: Path = (
            Path(__file__).parent.parent / "assets" / "images" / "ast"
        )

    @property
    def ast(self) -> str:
        """
        Get the current AST string representation.

        Returns:
            str: The current AST string representation.
        """
        return self._ast

    def create_ast(self, statement: Optional[Stmt]) -> None:
        """
        Generate the AST string representation for a given statement.

        Args:
            statement (Optional[Stmt]): The root statement to process.
                If None, sets empty string.
        """
        self._ast = statement.accept(self) if statement else ""

    def visualize_ast(self, statement_number: int = 0) -> None:
        """
        Create and save a visual representation of the AST as an image.

        Args:
            statement_number (int, optional): Identifier for the statement,
                used in output filename. Defaults to 0.
        """
        if not self._ast_directory_cleared:
            self._clear_ast_directory()
            self._ast_directory_cleared = True

        graph = AGraph(strict=True, directed=True)
        self._parse_expression(self._ast, graph)

        self._output_dir.mkdir(parents=True, exist_ok=True)
        output_file = self._output_dir / f"ast_statement_{statement_number}.png"

        graph.layout(prog="dot")
        graph.draw(str(output_file))
        print(f"AST image saved to {output_file}")

    def _clear_ast_directory(self) -> None:
        """
        Remove and recreate the AST output directory to ensure clean state.
        """
        if self._output_dir.exists():
            shutil.rmtree(self._output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def _split_expression(self, expr: str) -> List[str]:
        """
        Split a parenthesized AST string into its component parts.

        Args:
            expr (str): The AST string expression to split.

        Returns:
            List[str]: List of individual expression components.
        """
        parts: List[str] = []
        depth: int = 0
        current: str = ""
        in_string: bool = False

        for char in expr:
            if char == "(" and not in_string:
                if depth == 0 and current.strip():
                    parts.append(current.strip())
                    current = ""
                depth += 1
                current += char
            elif char == ")" and not in_string:
                depth -= 1
                current += char
                if depth == 0:
                    parts.append(current.strip())
                    current = ""
            elif char == '"':
                in_string = not in_string
                current += char
                if not in_string and depth == 0:
                    parts.append(current)
                    current = ""
            elif char == " " and depth == 0 and not in_string:
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
    ) -> None:
        """
        Recursively parse the AST string and construct the visualization graph.

        Args:
            expression (str): The expression segment to parse.
            graph (AGraph): The graph being constructed.
            parent (Optional[str], optional): The parent node ID if any. Defaults to None.
        """
        if self._node_counter > 1000:  # Prevent infinite recursion
            return

        expression = expression.strip()
        if not expression:
            return

        if expression.startswith("("):
            self._parse_parenthesized_expr(expression, graph, parent)
        else:
            self._parse_literal_expr(expression, graph, parent)

    def _parse_parenthesized_expr(
        self,
        expression: str,
        graph: AGraph,
        parent: Optional[str] = None,
    ) -> None:
        """
        Parse a parenthesized expression and add corresponding nodes to the graph.

        Args:
            expression (str): The parenthesized expression to parse.
            graph (AGraph): The graph being constructed.
            parent (Optional[str], optional): The parent node ID if any. Defaults to None.
        """
        expr_content = expression[1:-1].strip()
        space_idx = expr_content.find(" ")

        if expr_content.startswith('"') and expr_content.endswith('"'):
            operator = expr_content
            remaining = ""
        else:
            operator = expr_content[:space_idx] if space_idx != -1 else expr_content
            remaining = expr_content[space_idx + 1 :] if space_idx != -1 else ""

        node = self._create_graph_node(operator)
        if node.id in self._visited_nodes:
            return

        self._visited_nodes.add(node.id)
        graph.add_node(node.id, label=node.label)

        if parent:
            graph.add_edge(parent, node.id)

        if remaining:
            for child_expr in self._split_expression(remaining):
                self._parse_expression(child_expr, graph, node.id)

    def _parse_literal_expr(
        self,
        expression: str,
        graph: AGraph,
        parent: Optional[str] = None,
    ) -> None:
        """
        Parse a literal expression and add it to the visualization graph.

        Args:
            expression (str): The literal expression to parse.
            graph (AGraph): The graph being constructed.
            parent (Optional[str], optional): The parent node ID if any. Defaults to None.
        """
        node = self._create_graph_node(expression)
        graph.add_node(node.id, label=node.label)
        if parent:
            graph.add_edge(parent, node.id)

    def _create_graph_node(self, value: str) -> GraphNode:
        """
        Create a new graph node with appropriate labeling for visualization.

        Args:
            value (str): The value to create a node for.

        Returns:
            GraphNode: A new graph node instance with generated ID and label.
        """
        self._node_counter += 1
        node_id = f"node{self._node_counter}"

        if value.startswith('"') and value.endswith('"'):
            label = f"String: {value}"
        elif value.replace(".", "", 1).isdigit():
            label = f"Number: {value}"
        else:
            label = value

        return GraphNode(node_id, label)

    def _parenthesize(self, name: str, *exprs: Any) -> str:
        """
        Create a parenthesized string representation of an AST node.

        Args:
            name (str): The name of the AST node.
            *exprs (Any): The child expressions or tokens.

        Returns:
            str: Parenthesized string representation of the node.
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

    # Expression visitor methods
    def visit_binary_expr(self, expr: Binary) -> str:
        """
        Visit a binary expression node and create its string representation.

        Args:
            expr (Binary): The binary expression to visit.

        Returns:
            str: String representation of the binary expression.
        """
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_call_expr(self, expr: Call) -> str:
        """
        Visit a call expression node and create its string representation.

        Args:
            expr (Call): The call expression to visit.

        Returns:
            str: String representation of the call expression.
        """
        return self._parenthesize("call", expr.callee, *expr.arguments)

    def visit_get_expr(self, expr: Get) -> str:
        """
        Visit a get expression node and create its string representation.

        Args:
            expr (Get): The get expression to visit.

        Returns:
            str: String representation of the get expression.
        """
        return self._parenthesize(".", expr.object, expr.name.lexeme)

    def visit_grouping_expr(self, expr: Grouping) -> str:
        """
        Visit a grouping expression node and create its string representation.

        Args:
            expr (Grouping): The grouping expression to visit.

        Returns:
            str: String representation of the grouping expression.
        """
        return self._parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: Literal) -> str:
        """
        Visit a literal expression node and create its string representation.

        Args:
            expr (Literal): The literal expression to visit.

        Returns:
            str: String representation of the literal value.
        """
        if expr.value is None:
            return "nil"
        return f'"{expr.value}"' if isinstance(expr.value, str) else str(expr.value)

    def visit_logical_expr(self, expr: Logical) -> str:
        """
        Visit a logical expression node and create its string representation.

        Args:
            expr (Logical): The logical expression to visit.

        Returns:
            str: String representation of the logical expression.
        """
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_set_expr(self, expr: ExprSet) -> str:
        """
        Visit a set expression node and create its string representation.

        Args:
            expr (ExprSet): The set expression to visit.

        Returns:
            str: String representation of the set expression.
        """
        return self._parenthesize("set", expr.object, expr.name.lexeme, expr.value)

    def visit_super_expr(self, expr: Super) -> str:
        """
        Visit a super expression node and create its string representation.

        Args:
            expr (Super): The super expression to visit.

        Returns:
            str: String representation of the super expression.
        """
        return self._parenthesize("super", expr.method)

    def visit_this_expr(self, expr: This) -> str:
        """
        Visit a this expression node and create its string representation.

        Args:
            expr (This): The this expression to visit.

        Returns:
            str: The string "this".
        """
        return "this"

    def visit_unary_expr(self, expr: Unary) -> str:
        """
        Visit a unary expression node and create its string representation.

        Args:
            expr (Unary): The unary expression to visit.

        Returns:
            str: String representation of the unary expression.
        """
        return self._parenthesize(expr.operator.lexeme, expr.right)

    def visit_variable_expr(self, expr: Variable) -> str:
        """
        Visit a variable expression node and create its string representation.

        Args:
            expr (Variable): The variable expression to visit.

        Returns:
            str: The lexeme of the variable name.
        """
        return expr.name.lexeme

    def visit_assign_expr(self, expr: Assign) -> str:
        """
        Visit an assign expression node and create its string representation.

        Args:
            expr (Assign): The assign expression to visit.

        Returns:
            str: String representation of the assignment expression.
        """
        return self._parenthesize("=", expr.name.lexeme, expr.value)

    def visit_conditional_expr(self, expr: Conditional) -> str:
        """
        Visit a conditional (ternary) expression node and create its string representation.

        Args:
            expr (Conditional): The conditional expression to visit.

        Returns:
            str: String representation of the conditional expression.
        """
        return self._parenthesize(
            "?:", expr.condition, expr.then_branch, expr.else_branch
        )

    # Statement visitor methods
    def visit_expression_stmt(self, stmt: Expression) -> str:
        """
        Visit an expression statement node and create its string representation.

        Args:
            stmt (Expression): The expression statement to visit.

        Returns:
            str: String representation of the expression statement.
        """
        return self._parenthesize("expr", stmt.expression)

    def visit_print_stmt(self, stmt: Print) -> str:
        """
        Visit a print statement node and create its string representation.

        Args:
            stmt (Print): The print statement to visit.

        Returns:
            str: String representation of the print statement.
        """
        return self._parenthesize("print", stmt.expression)

    def visit_var_stmt(self, stmt: Var) -> str:
        """
        Visit a variable declaration node and create its string representation.

        Args:
            stmt (Var): The variable declaration to visit.

        Returns:
            str: String representation of the variable declaration.
        """
        return (
            self._parenthesize("var", stmt.name.lexeme, stmt.initializer)
            if stmt.initializer
            else self._parenthesize("var", stmt.name.lexeme)
        )

    def visit_block_stmt(self, stmt: Block) -> str:
        """
        Visit a block statement node and create its string representation.

        Args:
            stmt (Block): The block statement to visit.

        Returns:
            str: String representation of the block statement.
        """
        return self._parenthesize("block", *stmt.statements)

    def visit_if_stmt(self, stmt: If) -> str:
        """
        Visit an if statement node and create its string representation.

        Args:
            stmt (If): The if statement to visit.

        Returns:
            str: String representation of the if statement.
        """
        if stmt.else_branch:
            return self._parenthesize(
                "if", stmt.condition, stmt.then_branch, stmt.else_branch
            )
        return self._parenthesize("if", stmt.condition, stmt.then_branch)

    def visit_while_stmt(self, stmt: While) -> str:
        """
        Visit a while statement node and create its string representation.

        Args:
            stmt (While): The while statement to visit.

        Returns:
            str: String representation of the while statement.
        """
        return self._parenthesize("while", stmt.condition, stmt.body)

    def visit_break_stmt(self, stmt: Break) -> str:
        """
        Visit a break statement node and create its string representation.

        Args:
            stmt (Break): The break statement to visit.

        Returns:
            str: The string "(break)".
        """
        return "(break)"

    def visit_function_stmt(self, stmt: Function) -> str:
        """
        Visit a function declaration node and create its string representation.

        Args:
            stmt (Function): The function declaration to visit.

        Returns:
            str: String representation of the function declaration.
        """
        return self._parenthesize(f"fun {stmt.name.lexeme}", *stmt.body)

    def visit_return_stmt(self, stmt: Return) -> str:
        """
        Visit a return statement node and create its string representation.

        Args:
            stmt (Return): The return statement to visit.

        Returns:
            str: String representation of the return statement.
        """
        return self._parenthesize("return", stmt.value) if stmt.value else "(return)"

    def visit_trait_stmt(self, stmt: Trait) -> str:
        """
        Visit a trait declaration node and create its string representation.

        Args:
            stmt (Trait): The trait declaration to visit.

        Returns:
            str: String representation of the trait declaration.
        """
        parts = ["trait", stmt.name.lexeme]

        if stmt.traits:
            parts.extend(["with"] + [str(trait.accept(self)) for trait in stmt.traits])

        for method in stmt.methods:
            parts.append(self.visit_function_stmt(method))

        return self._parenthesize(*parts)

    def visit_class_stmt(self, stmt: Class) -> str:
        """
        Visit a class declaration node and create its string representation.

        Args:
            stmt (Class): The class declaration to visit.

        Returns:
            str: String representation of the class declaration.
        """
        parts = ["class", stmt.name.lexeme]
        if stmt.superclass:
            parts.extend(["inherits_from", stmt.superclass.name.lexeme])

        for method in stmt.methods:
            parts.append(self.visit_function_stmt(method))

        for class_method in stmt.class_methods:
            parts.append(
                self._parenthesize("class", self.visit_function_stmt(class_method))
            )

        return self._parenthesize(*parts)
