import os
from typing import List

from pygraphviz import AGraph

from expr import Binary, Expr, ExprVisitor, Grouping, Literal, Unary


class AstPrinter(ExprVisitor[str]):

    def __init__(self) -> None:
        self.ast: str = ""

    def create_ast(self, expr: Expr | None) -> None:
        if expr is None:
            self.ast = ""
            return

        self.ast = expr.accept(self)

    def visualize_ast(self) -> None:
        def _parse_expression(
            expression: str,
            graph: AGraph,
            parent: str | None = None,
            counter: List[int] = [0],
        ) -> None:

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

        # Ensure the .ast directory exists
        os.makedirs(ast_dir, exist_ok=True)

        # Filepath for the output image
        output_file = os.path.join(ast_dir, "ast_image.png")

        # Create and render the graph
        graph = AGraph(strict=True, directed=True)
        _parse_expression(self.ast, graph)
        graph.layout(prog="dot")
        graph.draw(output_file)
        print(f"AST image saved to {output_file}")

    def _parenthesize(self, name: str, *exprs: Expr) -> str:
        return f"({name} {' '.join(expr.accept(self) for expr in exprs)})"

    def visit_binary_expr(self, expr: Binary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_unary_expr(self, expr: Unary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.right)

    def visit_literal_expr(self, expr: Literal) -> str:
        return "nil" if expr.value is None else str(expr.value)

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self._parenthesize("group", expr.expression)
