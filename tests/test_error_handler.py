import unittest
from unittest.mock import patch

from lox.error_handler import (
    BreakException,
    ErrorHandler,
    LoxRuntimeError,
    ParseError,
    ReturnException,
)
from lox.tokens import Token, TokenType


class TestErrorHandler(unittest.TestCase):
    def setUp(self):
        self.handler = ErrorHandler()
        self.token = Token(TokenType.IDENTIFIER, "test", None, 1)

    def test_error_reporting(self):
        self.handler.error(1, "Test error")
        self.assertTrue(self.handler.had_error)
        self.assertEqual(self.handler.errors[0], "[1] Error: Test error")

        self.handler.error(self.token, "Token error")
        self.assertEqual(len(self.handler.errors), 2)

    def test_parse_error(self):
        with patch("builtins.print"):
            error = self.handler.parse_error(self.token, "Parse error")
            self.assertIsInstance(error, ParseError)
            self.assertEqual(error.token, self.token)
            self.assertTrue(self.handler.had_error)

    def test_print_all_errors(self):
        self.handler.error(1, "Error 1")
        self.handler.error(2, "Error 2")

        with patch("builtins.print") as mock_print:
            self.handler.print_all_errors()
            self.assertEqual(mock_print.call_count, 2)
            mock_print.assert_any_call("[1] Error: Error 1")
            mock_print.assert_any_call("[2] Error: Error 2")

    def test_reset(self):
        self.handler.error(1, "Test")
        self.handler.reset()
        self.assertFalse(self.handler.had_error)
        self.assertEqual(len(self.handler.errors), 0)

    def test_print_exception(self):
        with patch("builtins.print") as mock_print:
            with patch("traceback.print_exc") as mock_traceback:
                ErrorHandler.print_exception(Exception("Test"))
                mock_print.assert_called_with("Error: Test")
                mock_traceback.assert_called_once()


class TestExceptions(unittest.TestCase):
    def test_lox_runtime_error(self):
        token = Token(TokenType.IDENTIFIER, "test", None, 1)
        error = LoxRuntimeError(token, "Runtime error")
        self.assertEqual(str(error), "Runtime error")
        self.assertEqual(error.token, token)

    def test_parse_error(self):
        token = Token(TokenType.IDENTIFIER, "test", None, 1)
        error = ParseError(token, "Parse error")
        self.assertEqual(str(error), "Parse error")
        self.assertEqual(error.token, token)

    def test_return_exception(self):
        exception = ReturnException(42)
        self.assertEqual(exception.value, 42)

    def test_break_exception(self):
        exception = BreakException()
        self.assertIsInstance(exception, BreakException)


if __name__ == "__main__":
    unittest.main()
