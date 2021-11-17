import unittest

from compiler.parser import Parser
from compiler.semantics import SemanticAnalyzer
from compiler.tac import TACProcessor


class TestTac(unittest.TestCase):

    def _createTac(self, prog):
        self.parser = Parser(prog)
        root = self.parser.parseProgram(prog)
        semanticInstance = SemanticAnalyzer(root, self.parser.proglines)
        semanticInstance.checkSemantics()
        tac = TACProcessor(root)
        return tac.generateTAC()

    def testMultipleVar(self):
        prog = '''int a = 5;
        int b = 6;
        int c = a + b;
        '''
        lines = self._createTac(prog)
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], 'int a = 5')
        self.assertEqual(lines[1], 'int b = 6')
        self.assertEqual(lines[2], 't0 = a + b')
        self.assertEqual(lines[3], 'int c = t0')

    def testSumTac(self):
        lines = self._createTac('int a = 5 + 3 + 2;')
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], 't0 = 5 + 3')
        self.assertEqual(lines[1], 't1 = t0 + 2')
        self.assertEqual(lines[2], 'int a = t1')

    def testSubstractTac(self):
        lines = self._createTac('int a = 5 - 3 - 2;')
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], 't0 = 5 - 3')
        self.assertEqual(lines[1], 't1 = t0 - 2')
        self.assertEqual(lines[2], 'int a = t1')

    def testMultiplicationTac(self):
        lines = self._createTac('int a = 5 * 3 * 2;')
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], 't0 = 5 * 3')
        self.assertEqual(lines[1], 't1 = t0 * 2')
        self.assertEqual(lines[2], 'int a = t1')

    def testDivisionTac(self):
        lines = self._createTac('int a = 4 / 2 / 1;')
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], 't0 = 4 / 2')
        self.assertEqual(lines[1], 't1 = t0 / 1')
        self.assertEqual(lines[2], 'int a = t1')

    def testExponentTac(self):
        lines = self._createTac('int a = 4 ^ 2;')
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], 't0 = 4 ^ 2')
        self.assertEqual(lines[1], 'int a = t0')

    def testIntDcl(self):
        lines = self._createTac('int a = 2;')
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], 'int a = 2')

    def testFloatDcl(self):
        lines = self._createTac('float a = 2.0;')
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], 'float a = 2.0')

    def testStringDcl(self):
        lines = self._createTac('string a = "2";')
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], 'string a = 2')

    def testBoolDclT(self):
        lines = self._createTac('bool a = true;')
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], 'bool a = True')

    def testBoolDclF(self):
        lines = self._createTac('bool a = false;')
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], 'bool a = False')

    def testInt2FloatBasic(self):
        lines = self._createTac('float a = 1;')
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], 't0 = int2float(1)')
        self.assertEqual(lines[1], 'float a = t0')

    def testInt2Float(self):
        lines = self._createTac('float a = 1 + 2.0;')
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], 't0 = int2float(1)')
        self.assertEqual(lines[1], 't1 = t0 + 2.0')
        self.assertEqual(lines[2], 'float a = t1')

    def testPrecedence(self):
        prog = '''float a = 5 + 7.0;
        int b = 6;
        float c = a / b + (6 - 2) / 2 ^ 2;
        '''
        lines = self._createTac(prog)
        self.assertEqual(len(lines), 12)
        self.assertEqual(lines[0], 't0 = int2float(5)')
        self.assertEqual(lines[1], 't1 = t0 + 7.0')
        self.assertEqual(lines[2], 'float a = t1')
        self.assertEqual(lines[3], 'int b = 6')
        self.assertEqual(lines[4], 't2 = int2float(b)')
        self.assertEqual(lines[5], 't3 = a / t2')
        self.assertEqual(lines[6], 't4 = 6 - 2')
        self.assertEqual(lines[7], 't5 = 2 ^ 2')
        self.assertEqual(lines[8], 't6 = t4 / t5')
        self.assertEqual(lines[9], 't7 = int2float(t6)')
        self.assertEqual(lines[10], 't8 = t3 + t7')
        self.assertEqual(lines[11], 'float c = t8')
