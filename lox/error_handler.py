from __future__ import annotations

import traceback
from typing import Any, List, Optional, Union

from .tokens import Token


class BreakException(Exception):
    """
    Exception used to signal a break statement in loops.
    """

    ...


class LoxRuntimeError(RuntimeError):
    """
    Represents a runtime error in the Lox interpreter.

    Attributes:
        token (Token): The token where the error occurred.
    """

    __slots__ = ("token",)

    def __init__(self, token: Token, message: str) -> None:
        """
        Initialize a LoxRuntimeError with a specific token and message.

        Args:
            token (Token): The token where the error occurred.
            message (str): The error message.
        """
        super().__init__(message)
        self.token = token

    def __str__(self) -> str:
        """
        Return the string representation of the runtime error.

        Returns:
            str: The error message.
        """
        return super().__str__()

    def __repr__(self) -> str:
        """
        Return the official string representation of the runtime error.

        Returns:
            str: The official string representation.
        """
        return super().__repr__()


class ParseError(RuntimeError):
    """
    Represents a parsing error in the Lox interpreter.

    Attributes:
        token (Token): The token where the error occurred.
        error_handler (ErrorHandler): The handler for managing errors.
    """

    __slots__ = ("token", "error_handler")

    def __init__(self, token: Token, message: str) -> None:
        """
        Initialize a ParseError with a specific token and message.

        Args:
            token (Token): The token where the error occurred.
            message (str): The error message.
        """
        super().__init__(message)
        self.token: Token = token
        self.error_handler: ErrorHandler = ErrorHandler()


class ReturnException(Exception):
    """
    Exception used to signal a return statement in functions.

    Attributes:
        value (Any): The value to return from the function.
    """

    __slots__ = ("value",)

    def __init__(self, value: Any) -> None:
        """
        Initialize a ReturnException with a specific value.

        Args:
            value (Any): The value to return.
        """
        super().__init__()
        self.value = value


class ErrorHandler:
    """
    Handles errors encountered during interpretation and parsing.

    This class manages error reporting, storage, and displaying of errors.
    """

    __slots__ = ("errors", "had_error")

    def __init__(self) -> None:
        """
        Initialize the ErrorHandler with no errors.
        """
        self.errors: List[str] = []
        self.had_error: bool = False

    def error(self, line_or_token: Union[int, Token], message: str) -> None:
        """
        Report an error at a given line or token.

        Args:
            line_or_token (Union[int, Token]): The line number or token where the error occurred.
            message (str): The error message.
        """
        self.had_error = True
        self.errors.append(f"[{line_or_token}] Error: {message}")

    def parse_error(self, token: Token, message: str) -> ParseError:
        """
        Report a parse error and return a ParseError exception.

        Args:
            token (Token): The token where the error occurred.
            message (str): The error message.

        Returns:
            ParseError: The raised ParseError exception.
        """
        self.error(token.line, message)
        self.print_all_errors()
        return ParseError(token, message)

    def print_all_errors(self) -> None:
        """
        Print all recorded errors to the console.
        """
        for error in self.errors:
            print(error)

    def reset(self) -> None:
        """
        Reset the error handler by clearing all errors.
        """
        self.errors.clear()
        self.had_error = False

    @staticmethod
    def print_exception(exception: Exception) -> None:
        """
        Print an exception with its traceback.

        Args:
            exception (Exception): The exception to print.
        """
        print(f"Error: {exception}")
        print("Detailed traceback:")
        traceback.print_exc()
