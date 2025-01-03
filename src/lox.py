import sys
from parser import Parser
from pathlib import Path
from typing import List

from ast_printer import AstPrinter
from error_handler import ErrorHandler
from expr import Expr
from interpreter import Interpreter
from scanner import Scanner
from stmt import Stmt
from tokens import Token


def main() -> None:
    args = sys.argv[1:]
    error_handler = ErrorHandler()
    interpreter = Interpreter()

    if len(args) == 0:
        print("Lox REPL")
        run_prompt(error_handler, interpreter)
    elif len(args) == 1:
        run_file(args[0], error_handler, interpreter)
    else:
        print("Usage: [script] [file_path]")
        sys.exit(64)


def run_prompt(error_handler: ErrorHandler, interpreter: Interpreter) -> None:
    while True:
        try:
            line = input(">>> ")
            if not line.strip():
                break
            run(line, error_handler, interpreter)
            error_handler.reset()
        except EOFError:
            break
        except Exception as e:
            error_handler.print_exception(e)


def run_file(path: str, error_handler: ErrorHandler, interpreter: Interpreter) -> None:
    try:
        file_path = Path(path)

        if not file_path.exists():
            print(f"Error: File '{file_path}' not found.")
            return

        source = file_path.read_text(encoding="utf-8")
        run(source, error_handler, interpreter)

        if error_handler.had_error:
            sys.exit(65)

    except Exception as e:
        error_handler.print_exception(e)


def run(source: str, error_handler: ErrorHandler, interpreter: Interpreter) -> None:
    scanner = Scanner(source, error_handler)
    tokens: List[Token] = scanner.scan_tokens()
    parser: Parser = Parser(tokens, error_handler)
    statements: List[Stmt] = parser.parse()

    # ast_printer: AstPrinter = AstPrinter()
    # for token in tokens:
    #     print(
    #         f"TokenType: {token.type}, Lexeme: {token.lexeme}, Literal: {token.literal}, Line: {token.line}, PythonType: {type(token.literal)}"
    #     )
    # ast_printer.create_ast(expression)
    # ast_printer.visualize_ast()

    if error_handler.had_error:
        error_handler.print_all_errors()

    assert interpreter is not None
    interpreter.interpret(statements)


if __name__ == "__main__":
    main()
