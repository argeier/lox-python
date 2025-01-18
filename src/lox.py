import shutil
import sys
from parser import Parser
from pathlib import Path
from typing import List, Optional

from ast_printer import AstPrinter
from error_handler import ErrorHandler
from interpreter import Interpreter
from scanner import Scanner
from stmt import Stmt
from tokens import Token


def main() -> None:
    """
    The main entry point of the Lox interpreter. Parses command-line arguments
    to determine whether to run in REPL mode or execute a script file. Additionally,
    it handles the optional AST printing functionality when the '-ast' flag is provided.
    """
    args = sys.argv[1:]
    error_handler = ErrorHandler()
    interpreter = Interpreter()
    ast_enabled = False

    # Check for '-ast' flag and remove it from arguments if present
    if "-ast" in args:
        ast_enabled = True
        args.remove("-ast")

    if len(args) == 0:
        print("Lox REPL")
        run_prompt(error_handler, interpreter, ast_enabled)
    elif len(args) == 1:
        run_file(args[0], error_handler, interpreter, ast_enabled)
    else:
        print("Usage: lox.py [-ast] [script]")
        sys.exit(64)


def run_prompt(
    error_handler: ErrorHandler, interpreter: Interpreter, ast_enabled: bool
) -> None:
    """
    Runs the Lox interpreter in REPL (Read-Eval-Print Loop) mode.

    Args:
        error_handler (ErrorHandler): The error handler instance.
        interpreter (Interpreter): The interpreter instance.
        ast_enabled (bool): Flag indicating whether AST printing is enabled.
    """
    while True:
        try:
            line = input(">>> ")
            if not line.strip():
                continue  # Continue REPL on empty input
            run(line, error_handler, interpreter, ast_enabled)
            error_handler.reset()
        except EOFError:
            print("\nExiting Lox REPL.")
            break
        except Exception as e:
            error_handler.print_exception(e)


def run_file(
    path: str, error_handler: ErrorHandler, interpreter: Interpreter, ast_enabled: bool
) -> None:
    """
    Executes a Lox script from the specified file.

    Args:
        path (str): The file path to the Lox script.
        error_handler (ErrorHandler): The error handler instance.
        interpreter (Interpreter): The interpreter instance.
        ast_enabled (bool): Flag indicating whether AST printing is enabled.
    """
    try:
        file_path = Path(path)

        if not file_path.exists():
            print(f"Error: File '{file_path}' not found.")
            sys.exit(66)  # Exit code 66 for no input file

        source = file_path.read_text(encoding="utf-8")
        run(source, error_handler, interpreter, ast_enabled)

        if error_handler.had_error:
            sys.exit(65)  # Exit code 65 for data format error

    except Exception as e:
        error_handler.print_exception(e)
        sys.exit(70)  # Exit code 70 for internal software error


def run(
    source: str,
    error_handler: ErrorHandler,
    interpreter: Interpreter,
    ast_enabled: bool,
) -> None:
    """
    Processes the source code by scanning, parsing, optionally printing the AST,
    and interpreting the statements.

    Args:
        source (str): The Lox source code.
        error_handler (ErrorHandler): The error handler instance.
        interpreter (Interpreter): The interpreter instance.
        ast_enabled (bool): Flag indicating whether AST printing is enabled.
    """
    scanner = Scanner(source, error_handler)
    tokens: List[Token] = scanner.scan_tokens()
    parser = Parser(tokens, error_handler)
    statements: List[Stmt] = parser.parse()

    if error_handler.had_error:
        error_handler.print_all_errors()
        return

    if ast_enabled:
        printer = AstPrinter()
        for i, statement in enumerate(statements):
            printer.create_ast(statement)
            printer.visualize_ast(i)

    interpreter.interpret(statements)


if __name__ == "__main__":
    main()
