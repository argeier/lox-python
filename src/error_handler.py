import traceback
from typing import List

from tokens import Token


class ParseError(RuntimeError):

    def __init__(self, token: Token, message: str) -> None:
        super().__init__(message)
        self.token: Token = token
        self.error_handler: ErrorHandler = ErrorHandler()


class ErrorHandler:

    def __init__(self) -> None:
        self.errors: List[str] = []
        self.had_error: bool = False

    def error(self, line: int, message: str) -> None:
        self.had_error = True
        self.errors.append(f"[line {line}] Error: {message}")

    def parse_error(self, token: Token, message: str) -> ParseError:
        self.error(token.line, message)
        self.print_all_errors()
        return ParseError(token, message)

    def print_all_errors(self) -> None:
        for error in self.errors:
            print(error)

    def reset(self) -> None:
        self.errors.clear()
        self.had_error = False

    @staticmethod
    def print_exception(exception: Exception) -> None:
        print(f"Error: {exception}")
        print("Detailed traceback:")
        traceback.print_exc()
