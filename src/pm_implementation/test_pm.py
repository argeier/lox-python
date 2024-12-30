import sys
import time
import tracemalloc

sys.path.append(".")

from ast_printer_pm import AstPrinter as PMAstPrinter
from tmp.expr_pm import Binary as PMBinary
from tmp.expr_pm import Grouping as PMGrouping
from tmp.expr_pm import Literal as PMLiteral
from tmp.expr_pm import Unary as PMUnary

from src.ast_printer import AstPrinter as VisitorAstPrinter
from src.expr import Binary, Grouping, Literal, Unary
from src.tokens import Token, TokenType


def create_complex_expression():
    """Creates a complex expression using the visitor pattern classes."""
    return Binary(
        Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(
            Binary(Literal(45.67), Token(TokenType.PLUS, "+", None, 1), Literal(89))
        ),
    )


def create_complex_expression_pm():
    """Creates a complex expression using the pattern-matching classes."""
    return PMBinary(
        PMUnary("-", PMLiteral(123)),
        "*",
        PMGrouping(PMBinary(PMLiteral(45.67), "+", PMLiteral(89))),
    )


def measure_execution_time_and_memory(func):
    """Measures both execution time and memory usage."""
    tracemalloc.start()
    start_time = time.perf_counter()
    func()
    execution_time = time.perf_counter() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return execution_time, current, peak


def visitor_test():
    """Test function for the visitor pattern."""
    expr = create_complex_expression()
    printer = VisitorAstPrinter()
    for _ in range(10000):
        printer.print(expr)


def pm_test():
    """Test function for the pattern-matching approach."""
    expr = create_complex_expression_pm()
    printer = PMAstPrinter()
    for _ in range(10000):
        printer.print(expr)


if __name__ == "__main__":
    visitor_time, visitor_memory_current, visitor_memory_peak = (
        measure_execution_time_and_memory(visitor_test)
    )
    pm_time, pm_memory_current, pm_memory_peak = measure_execution_time_and_memory(
        pm_test
    )

    print("Performance and Memory Usage Comparison")
    print("----------------------------------------")
    print(f"Visitor Pattern:")
    print(f"  Execution Time: {visitor_time:.6f} seconds")
    print(
        f"  Memory Usage: {visitor_memory_current / 1024:.2f} KB (current), {visitor_memory_peak / 1024:.2f} KB (peak)"
    )
    print()
    print(f"Pattern Matching:")
    print(f"  Execution Time: {pm_time:.6f} seconds")
    print(
        f"  Memory Usage: {pm_memory_current / 1024:.2f} KB (current), {pm_memory_peak / 1024:.2f} KB (peak)"
    )

# Found the visitor pattern to be not very intuitive, contrary to pattern matching
# in e.g. Haskell, which is why i wanted to atleast implement the PM variant and
# benchmark this approach

# results of benchmark
# ❯ python test_pm.py
# Performance and Memory Usage Comparison
# ----------------------------------------
# Visitor Pattern:
#   Execution Time: 0.110892 seconds
#   Memory Usage: 0.00 KB (current), 5.08 KB (peak)

# Pattern Matching:
#   Execution Time: 0.129540 seconds
#   Memory Usage: 66.01 KB (current), 68.84 KB (peak)
