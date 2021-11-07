import unittest

from compiler.lexer import Lexer, LexerTypes


class TestLexer(unittest.TestCase):

    def setUp(self):
        instance = Lexer()
        self.lexer = instance.createLexer()

    def _getTokens(self, input: str):
        self.lexer.input(input)
        results = []
        while True:
            token = self.lexer.token()
            if not token:
                break
            results.append(token)
        return results

    def _testSingleToken(self, input: str, typeValue: str):
        token = self._getTokens(input)[0]
        self.assertEqual(token.type, typeValue)

    def testEqual(self):
        self._testSingleToken('=', '=')

    def testPlus(self):
        self._testSingleToken('+', '+')

    def testMinus(self):
        self._testSingleToken('-', '-')

    def testMultiplication(self):
        self._testSingleToken('*', '*')

    def testDivision(self):
        self._testSingleToken('/', '/')

    def testLeftParenthesis(self):
        self._testSingleToken('(', '(')

    def testRightParenthesis(self):
        self._testSingleToken(')', ')')

    def testName(self):
        self._testSingleToken('variable', LexerTypes.NAME.name)

    def testIntDlc(self):
        self._testSingleToken('int', LexerTypes.INTDCL.name)

    def testFloatDlc(self):
        self._testSingleToken('float', LexerTypes.FLOATDCL.name)

    def testPrint(self):
        self._testSingleToken('print', LexerTypes.PRINT.name)

    def testIntNumber(self):
        self._testSingleToken('12', LexerTypes.INTNUM.name)

    def testFloatNumber(self):
        self._testSingleToken('1.2', LexerTypes.FLOATNUM.name)

    def testInvalidCharacter(self):
        tokens = self._getTokens('?')
        self.assertEqual(len(tokens), 0)


if __name__ == '__main__':
    unittest.main()
