import unittest

from src.lox.tokens import KEYWORDS, Token, TokenType


class TestTokenType(unittest.TestCase):
    def test_token_type_values(self):
        self.assertEqual(TokenType.LEFT_PAREN.value, "(")
        self.assertEqual(TokenType.RIGHT_PAREN.value, ")")
        self.assertEqual(TokenType.IDENTIFIER.value, "IDENTIFIER")
        self.assertEqual(TokenType.FUN.value, "fun")
        self.assertEqual(TokenType.BREAK.value, "break")
        self.assertEqual(TokenType.EOF.value, "EOF")


class TestToken(unittest.TestCase):
    def test_token_initialization(self):
        token = Token(TokenType.IDENTIFIER, "varName", None, 1)
        self.assertEqual(token.type, TokenType.IDENTIFIER)
        self.assertEqual(token.lexeme, "varName")
        self.assertIsNone(token.literal)
        self.assertEqual(token.line, 1)

    def test_token_str(self):
        token = Token(TokenType.NUMBER, "123", 123, 1)
        self.assertEqual(str(token), "TokenType.NUMBER 123 123")


class TestKeywords(unittest.TestCase):
    def test_keywords_mapping(self):
        self.assertEqual(KEYWORDS["and"], TokenType.AND)
        self.assertEqual(KEYWORDS["class"], TokenType.CLASS)
        self.assertEqual(KEYWORDS["fun"], TokenType.FUN)
        self.assertEqual(KEYWORDS["break"], TokenType.BREAK)
        self.assertNotIn("nonexistent", KEYWORDS)


if __name__ == "__main__":
    unittest.main()
