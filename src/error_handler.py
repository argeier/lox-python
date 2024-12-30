import traceback
from typing import List

from tokens import Token


class ParseError(RuntimeError):
    """
    A custom exception raised during the parsing phase.

    Attributes:
        token (Token): The token where the error occurred.
        message (str): The error message.
        error_handler (ErrorHandler): The error handler associated with this error.
    """

    def __init__(self, token: Token, message: str) -> None:
        """
        Initializes the ParseError with a token, message, and an associated error handler.

        Args:
            token (Token): The token where the error occurred.
            message (str): The error message.
        """
        super().__init__(message)
        self.token: Token = token
        self.error_handler: ErrorHandler = ErrorHandler()


class ErrorHandler:
    """
    A class for handling errors encountered during the scanning or parsing phase.

    Attributes:
        errors (List[str]): A list of error messages.
        had_error (bool): A flag indicating if an error has occurred.
    """

    def __init__(self) -> None:
        """
        Initializes the ErrorHandler with an empty error list and no error flag.
        """
        self.errors: List[str] = []
        self.had_error: bool = False

    def error(self, line: int, message: str) -> None:
        """
        Records an error message and sets the error flag.

        Args:
            line (int): The line number where the error occurred.
            message (str): The error message to record.
        """
        self.had_error = True
        self.errors.append(f"[line {line}] Error: {message}")

    def parse_error(self, token: Token, message: str) -> ParseError:
        """
        Records a parse error and returns a ParseError exception.

        Args:
            token (Token): The token where the error occurred.
            message (str): The error message to record.

        Returns:
            ParseError: The generated parse error exception.
        """
        self.error(token.line, message)
        self.print_all_errors()
        return ParseError(token, message)

    def print_all_errors(self) -> None:
        """
        Prints all recorded error messages to the console.
        """
        for error in self.errors:
            print(error)

    def reset(self) -> None:
        """
        Resets the error handler by clearing all recorded errors and resetting the error flag.
        """
        self.errors.clear()
        self.had_error = False

    @staticmethod
    def print_exception(exception: Exception) -> None:
        """
        Prints detailed information about an exception, including the traceback.

        Args:
            exception (Exception): The exception to print.
        """
        print(f"Error: {exception}")
        print("Detailed traceback:")
        traceback.print_exc()
