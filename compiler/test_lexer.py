import unittest

from compiler.lexer import Lexer, LexerTypes


class TestLexer(unittest.TestCase):

    def setUp(self):
        self.instance = Lexer()
        self.lexer = self.instance.createLexer()

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
        self.assertEqual(self.instance.n_errors, 0)

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

    def testExponent(self):
        self._testSingleToken('^', '^')

    def testGreaterThan(self):
        self._testSingleToken('>', '>')

    def testLessThan(self):
        self._testSingleToken('<', '<')

    def testLeftParenthesis(self):
        self._testSingleToken('(', '(')

    def testRightParenthesis(self):
        self._testSingleToken(')', ')')

    def testLeftBracket(self):
        self._testSingleToken('{', '{')

    def testRightBracket(self):
        self._testSingleToken('}', '}')

    def testSentenceEnd(self):
        self._testSingleToken(';', LexerTypes.SENTENCE_END.name)

    def testComparisonEquals(self):
        self._testSingleToken('==', LexerTypes.EQUALS.name)

    def testComparisonNotEqual(self):
        self._testSingleToken('!=', LexerTypes.NOT_EQUAL.name)

    def testComparisonGreaterEqual(self):
        self._testSingleToken('>=', LexerTypes.GREATER_EQUAL.name)

    def testComparisonLessEqual(self):
        self._testSingleToken('<=', LexerTypes.LESS_EQUAL.name)

    def testAndOperator(self):
        self._testSingleToken('and', LexerTypes.AND_OP.name)

    def testOrOperator(self):
        self._testSingleToken('or', LexerTypes.OR_OP.name)

    def testName(self):
        self._testSingleToken('variable', LexerTypes.NAME.name)

    def testIntDlc(self):
        self._testSingleToken('int', LexerTypes.INTDCL.name)

    def testFloatDlc(self):
        self._testSingleToken('float', LexerTypes.FLOATDCL.name)

    def testStringDcl(self):
        self._testSingleToken('string', LexerTypes.STRING_DCL.name)

    def testBooleanDcl(self):
        self._testSingleToken('bool', LexerTypes.BOOL_DCL.name)

    def testPrint(self):
        self._testSingleToken('print', LexerTypes.PRINT.name)

    def testFor(self):
        self._testSingleToken('for', LexerTypes.FOR.name)

    def testWhile(self):
        self._testSingleToken('while', LexerTypes.WHILE.name)

    def testIf(self):
        self._testSingleToken('if', LexerTypes.IF.name)

    def testElif(self):
        self._testSingleToken('elif', LexerTypes.ELIF.name)

    def testElse(self):
        self._testSingleToken('else', LexerTypes.ELSE.name)

    def testIntNumber(self):
        self._testSingleToken('12', LexerTypes.INTNUM.name)

    def testFloatNumber(self):
        self._testSingleToken('1.2', LexerTypes.FLOATNUM.name)

    def testTrue(self):
        self._testSingleToken('true', LexerTypes.BOOL_TRUE.name)

    def testFalse(self):
        self._testSingleToken('false', LexerTypes.BOOL_FALSE.name)

    def testInvalidCharacter(self):
        tokens = self._getTokens('?')
        self.assertEqual(len(tokens), 0)


if __name__ == '__main__':
    unittest.main()
