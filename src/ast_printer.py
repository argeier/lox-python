import os
from typing import List, Optional, override

from pygraphviz import AGraph

from expr import Binary, Expr, Grouping, Literal, Unary, Visitor


class AstPrinter(Visitor[str]):
    """
    A visitor that converts an abstract syntax tree (AST) into a string representation
    and visualizes it as an image.
    """

    def __init__(self) -> None:
        """
        Initializes the AstPrinter with an empty AST string.
        """
        self.ast: str = ""

    def create_ast(self, expr: Expr | None) -> None:
        """
        Generates the string representation of the AST.

        Args:
            expr (Expr): The root expression of the AST.
        """
        if expr is None:
            self.ast = ""
            return

        self.ast = expr.accept(self)

    def _parenthesize(self, name: str, *exprs: Expr) -> str:
        """
        Creates a parenthesized string representation for an operator and its operands.

        Args:
            name (str): The operator name.
            *exprs (Expr): The operand expressions.

        Returns:
            str: A parenthesized string representation of the expression.
        """
        return f"({name} {' '.join(expr.accept(self) for expr in exprs)})"

    @override
    def visit_binary_expr(self, expr: Expr) -> str:
        """
        Visits a binary expression and generates its string representation.

        Args:
            expr (Binary): The binary expression.

        Returns:
            str: The string representation of the binary expression.
        """
        assert isinstance(expr, Binary)
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    @override
    def visit_unary_expr(self, expr: Expr) -> str:
        """
        Visits a unary expression and generates its string representation.

        Args:
            expr (Unary): The unary expression.

        Returns:
            str: The string representation of the unary expression.
        """
        assert isinstance(expr, Unary)
        return self._parenthesize(expr.operator.lexeme, expr.right)

    @override
    def visit_literal_expr(self, expr: Expr) -> str:
        """
        Visits a literal expression and generates its string representation.

        Args:
            expr (Literal): The literal expression.

        Returns:
            str: The string representation of the literal expression.
        """
        assert isinstance(expr, Literal)
        return "nil" if expr.value is None else str(expr.value)

    @override
    def visit_grouping_expr(self, expr: Expr) -> str:
        """
        Visits a grouping expression and generates its string representation.

        Args:
            expr (Grouping): The grouping expression.

        Returns:
            str: The string representation of the grouping expression.
        """
        assert isinstance(expr, Grouping)
        return self._parenthesize("group", expr.expression)

    def visualize_ast(self) -> None:
        """
        Visualizes the AST as a PNG image and saves it to the `.ast` directory within the project root.
        """

        def _parse_expression(
            expression: str,
            graph: AGraph,
            parent: Optional[str] = None,
            counter: List[int] = [0],
        ) -> None:
            """
            Recursively parses the AST string and constructs the graph.

            Args:
                expression (str): The string representation of the AST.
                graph (AGraph): The graph object to populate.
                parent (Optional[str]): The parent node ID. Defaults to None.
                counter (List[int]): A counter to generate unique node IDs. Defaults to [0].
            """
            expression = expression.strip()
            if expression.startswith("("):
                end_operator_idx = expression.find(" ")
                operator = expression[1:end_operator_idx]
                node_id = f"node{counter[0]}"
                counter[0] += 1
                graph.add_node(node_id, label=operator)
                if parent:
                    graph.add_edge(parent, node_id)

                remaining = expression[end_operator_idx + 1 : -1].strip()
                while remaining:
                    if remaining.startswith("("):  # Sub-expression is a group
                        open_count = 0
                        for i, char in enumerate(remaining):
                            if char == "(":
                                open_count += 1
                            elif char == ")":
                                open_count -= 1
                            if open_count == 0:
                                sub_expression = remaining[: i + 1]
                                _parse_expression(
                                    sub_expression, graph, node_id, counter
                                )
                                remaining = remaining[i + 1 :].strip()
                                break
                    else:  # Sub-expression is a literal or identifier
                        space_idx = remaining.find(" ")
                        if space_idx == -1:  # Last element
                            sub_expression = remaining
                            remaining = ""
                        else:
                            sub_expression = remaining[:space_idx]
                            remaining = remaining[space_idx + 1 :].strip()
                        leaf_id = f"node{counter[0]}"
                        counter[0] += 1
                        graph.add_node(leaf_id, label=sub_expression)
                        graph.add_edge(node_id, leaf_id)
            else:  # Single literal or identifier
                leaf_id = f"node{counter[0]}"
                counter[0] += 1
                graph.add_node(leaf_id, label=expression)
                if parent:
                    graph.add_edge(parent, leaf_id)

        # Determine the project root based on the location of this script
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ast_dir = os.path.join(project_root, ".ast")

        # Ensure the `.ast` directory exists
        os.makedirs(ast_dir, exist_ok=True)

        # Filepath for the output image
        output_file = os.path.join(ast_dir, "ast_image.png")

        # Create and render the graph
        graph = AGraph(strict=True, directed=True)
        _parse_expression(self.ast, graph)
        graph.layout(prog="dot")
        graph.draw(output_file)
        print(f"AST image saved to {output_file}")
