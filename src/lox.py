import sys
from parser import Parser
from pathlib import Path
from typing import List

from ast_printer import AstPrinter
from error_handler import ErrorHandler
from expr import Expr
from scanner import Scanner
from tokens import Token, TokenType


def main() -> None:
    """
    Entry point of the script. Handles command-line arguments and delegates to prompt or file mode.
    """
    args = sys.argv[1:]
    error_handler = ErrorHandler()

    if len(args) == 0:
        print("PROMPT")
        run_prompt(error_handler)
    elif len(args) == 1:
        print("FILE")
        run_file(args[0], error_handler)
    else:
        print("Usage: [script] [file_path]")
        sys.exit(64)


def run_prompt(error_handler: ErrorHandler) -> None:
    """
    Interactive prompt mode for running the scanner.

    Args:
        error_handler (ErrorHandler): Instance to handle errors during execution.
    """
    while True:
        try:
            line = input("> ")
            if not line.strip():
                break
            run(line, error_handler)
            error_handler.reset()
        except EOFError:
            break
        except Exception as e:
            error_handler.print_exception(e)


def run_file(path: str, error_handler: ErrorHandler) -> None:
    """
    Reads source code from a file and processes it using the scanner.

    Args:
        path (str): Path to the file to scan.
        error_handler (ErrorHandler): Instance to handle errors during execution.
    """
    try:
        file_path = Path(path)

        if not file_path.exists():
            print(f"Error: File '{file_path}' not found.")
            return

        source = file_path.read_text(encoding="utf-8")
        run(source, error_handler)

        if error_handler.had_error:
            sys.exit(65)

    except Exception as e:
        error_handler.print_exception(e)


def run(source: str, error_handler: ErrorHandler) -> None:
    """
    Executes the scanner on the provided source code.

    Args:
        source (str): The source code to scan.
        error_handler (ErrorHandler): Instance to handle errors during execution.
    """
    scanner = Scanner(source, error_handler)
    tokens: List[Token] = scanner.scan_tokens()
    parser: Parser = Parser(tokens, error_handler)
    expression: Expr = parser.parse()
    ast_printer: AstPrinter = AstPrinter()

    for token in tokens:
        print(
            f"TokenType: {token.type}, Lexeme: {token.lexeme}, Literal: {token.literal}, Line: {token.line}"
        )

    ast_printer.create_ast(expression)
    print(ast_printer.ast)
    ast_printer.visualize_ast()

    if error_handler.had_error:
        error_handler.print_all_errors()


if __name__ == "__main__":
    main()
