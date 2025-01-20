import sys
from pathlib import Path
from typing import List

from .ast_printer import AstPrinter
from .error_handler import ErrorHandler
from .interpreter import Interpreter
from .parser import Parser
from .resolver import Resolver
from .scanner import Scanner
from .stmt import Stmt
from .tokens import Token


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
    Runs the Lox interpreter in REPL (Read-Eval-Print Loop) mode with support for:
    - Multi-line input for blocks and functions
    - Input history tracking
    - Proper error recovery
    - Better visual formatting

    Args:
        error_handler (ErrorHandler): The error handler instance.
        interpreter (Interpreter): The interpreter instance.
        ast_enabled (bool): Flag indicating whether AST printing is enabled.
    """
    current_input = []
    open_braces = 0
    open_parens = 0
    in_string = False

    print("Lox REPL - Type 'exit()' to quit")
    print("Enter your code. For multi-line input, press Enter after an opening brace.")

    while True:
        try:
            # Determine the prompt based on context
            if not current_input:
                prompt = ">>> "
            else:
                prompt = "... "

            # Get input line
            line = input(prompt)

            # Handle exit command
            if line.strip() == "exit()":
                print("\nExiting Lox REPL.")
                break

            # Skip empty lines at the start
            if not current_input and not line.strip():
                continue

            # Update brace/parenthesis/string counters
            for char in line:
                if char == '"' and not in_string:
                    in_string = True
                elif char == '"' and in_string:
                    in_string = False
                elif not in_string:
                    if char == "{":
                        open_braces += 1
                    elif char == "}":
                        open_braces = max(0, open_braces - 1)
                    elif char == "(":
                        open_parens += 1
                    elif char == ")":
                        open_parens = max(0, open_parens - 1)

            # Add line to current input
            current_input.append(line)

            # If we have a complete input (all braces/parentheses matched and not in a string)
            if not open_braces and not open_parens and not in_string:
                # Join all lines and check if there's actual content
                source = "\n".join(current_input).strip()
                if source:
                    try:
                        run(source, error_handler, interpreter, ast_enabled)
                    except Exception as e:
                        error_handler.print_exception(e)
                    finally:
                        error_handler.reset()

                # Reset for next input
                current_input = []
                open_braces = 0
                open_parens = 0
                in_string = False

        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
            current_input = []
            open_braces = 0
            open_parens = 0
            in_string = False
        except EOFError:
            print("\nExiting Lox REPL.")
            break


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

    resolver: Resolver = Resolver(interpreter, error_handler)
    resolver.resolve(statements)

    if error_handler.had_error:
        error_handler.print_all_errors()
        return

    interpreter.interpret(statements)


if __name__ == "__main__":
    main()
