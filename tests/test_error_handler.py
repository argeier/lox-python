import unittest
from unittest.mock import patch

from src.lox.error_handler import (
    BreakException,
    ErrorHandler,
    LoxRuntimeError,
    ParseError,
    ReturnException,
)
from src.lox.tokens import Token, TokenType


class TestErrorHandler(unittest.TestCase):
    def setUp(self):
        self.error_handler = ErrorHandler()

    def test_error(self):
        self.error_handler.error(1, "Test error")
        self.assertTrue(self.error_handler.had_error)
        self.assertIn("[line or token 1] Error: Test error", self.error_handler.errors)

    def test_parse_error(self):
        token = Token(TokenType.IDENTIFIER, "test", None, 1)
        with patch("builtins.print") as mock_print:
            parse_error = self.error_handler.parse_error(token, "Parse error")
            self.assertTrue(self.error_handler.had_error)
            self.assertIn(
                "[line or token 1] Error: Parse error", self.error_handler.errors
            )
            mock_print.assert_called_with("[line or token 1] Error: Parse error")
            self.assertIsInstance(parse_error, ParseError)
            self.assertEqual(parse_error.token, token)

    def test_print_all_errors(self):
        self.error_handler.error(1, "Test error 1")
        self.error_handler.error(2, "Test error 2")
        with patch("builtins.print") as mock_print:
            self.error_handler.print_all_errors()
            mock_print.assert_any_call("[line or token 1] Error: Test error 1")
            mock_print.assert_any_call("[line or token 2] Error: Test error 2")

    def test_reset(self):
        self.error_handler.error(1, "Test error")
        self.error_handler.reset()
        self.assertFalse(self.error_handler.had_error)
        self.assertEqual(len(self.error_handler.errors), 0)

    def test_print_exception(self):
        exception = Exception("Test exception")
        with patch("builtins.print") as mock_print:
            with patch("traceback.print_exc") as mock_print_exc:
                ErrorHandler.print_exception(exception)
                mock_print.assert_any_call("Error: Test exception")
                mock_print_exc.assert_called_once()


class TestLoxRuntimeError(unittest.TestCase):

    def test_lox_runtime_error(self):
        token = Token(TokenType.IDENTIFIER, "test", None, 1)
        error = LoxRuntimeError(token, "Runtime error")
        self.assertEqual(str(error), "Runtime error")
        self.assertEqual(repr(error), "LoxRuntimeError('Runtime error')")
        self.assertEqual(error.token, token)


class TestParseError(unittest.TestCase):
    def test_parse_error(self):
        token = Token(TokenType.IDENTIFIER, "test", None, 1)
        error = ParseError(token, "Parse error")
        self.assertEqual(str(error), "Parse error")
        self.assertEqual(error.token, token)


class TestReturnException(unittest.TestCase):
    def test_return_exception(self):
        value = 123
        exception = ReturnException(value)
        self.assertEqual(exception.value, value)


class TestBreakException(unittest.TestCase):
    def test_break_exception(self):
        exception = BreakException()
        self.assertIsInstance(exception, BreakException)


if __name__ == "__main__":
    unittest.main()
