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
        self.assertEqual(len(lines), 7)
        self.assertEqual(lines[0], 'declareint a')
        self.assertEqual(lines[1], 'a = 5')
        self.assertEqual(lines[2], 'declareint b')
        self.assertEqual(lines[3], 'b = 6')
        self.assertEqual(lines[4], 't0 = a + b')
        self.assertEqual(lines[5], 'declareint c')
        self.assertEqual(lines[6], 'c = t0')

    def testSumTac(self):
        lines = self._createTac('int a = 5 + 3 + 2;')
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], 't0 = 5 + 3')
        self.assertEqual(lines[1], 't1 = t0 + 2')
        self.assertEqual(lines[2], 'declareint a')
        self.assertEqual(lines[3], 'a = t1')

    def testSubstractTac(self):
        lines = self._createTac('int a = 5 - 3 - 2;')
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], 't0 = 5 - 3')
        self.assertEqual(lines[1], 't1 = t0 - 2')
        self.assertEqual(lines[2], 'declareint a')
        self.assertEqual(lines[3], 'a = t1')

    def testMultiplicationTac(self):
        lines = self._createTac('int a = 5 * 3 * 2;')
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], 't0 = 5 * 3')
        self.assertEqual(lines[1], 't1 = t0 * 2')
        self.assertEqual(lines[2], 'declareint a')
        self.assertEqual(lines[3], 'a = t1')

    def testDivisionTac(self):
        lines = self._createTac('int a = 4 / 2 / 1;')
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], 't0 = 4 / 2')
        self.assertEqual(lines[1], 't1 = t0 / 1')
        self.assertEqual(lines[2], 'declareint a')
        self.assertEqual(lines[3], 'a = t1')

    def testExponentTac(self):
        lines = self._createTac('int a = 4 ^ 2;')
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], 't0 = 4 ^ 2')
        self.assertEqual(lines[1], 'declareint a')
        self.assertEqual(lines[2], 'a = t0')

    def testBoolAlgebra(self):
        lines = self._createTac(
            'bool a = (2 > 2) and (2 >= 2) or (2 < 2) and (2 <= 2) or (2 == 2) and (2 != 2);')
        expectedLines = '''t0 = 2 > 2
        t1 = 2 >= 2
        t2 = t0 and t1
        t3 = 2 < 2
        t4 = t2 or t3
        t5 = 2 <= 2
        t6 = t4 and t5
        t7 = 2 == 2
        t8 = t6 or t7
        t9 = 2 != 2
        t10 = t8 and t9
        declarebool a
        a = t10
        '''
        expectedLines = expectedLines.split('\n')
        for i in range(len(expectedLines)):
            expectedLines[i] = expectedLines[i].strip()
        self.assertEqual(len(lines), 13)
        for i in range(len(lines)):
            self.assertEqual(lines[i], expectedLines[i])

    def testIntDcl(self):
        lines = self._createTac('int a = 2;')
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], 'declareint a')
        self.assertEqual(lines[1], 'a = 2')

    def testFloatDcl(self):
        lines = self._createTac('float a = 2.0;')
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], 'declarefloat a')
        self.assertEqual(lines[1], 'a = 2.0')

    def testStringDcl(self):
        lines = self._createTac('string a = "b";')
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], 'declarestring a')
        self.assertEqual(lines[1], 'a = "b"')

    def testBoolDclT(self):
        lines = self._createTac('bool a = true;')
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], 'declarebool a')
        self.assertEqual(lines[1], 'a = True')

    def testBoolDclF(self):
        lines = self._createTac('bool a = false;')
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], 'declarebool a')
        self.assertEqual(lines[1], 'a = False')

    def testInt2FloatBasic(self):
        lines = self._createTac('float a = 1;')
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], 't0 = toFloat 1')
        self.assertEqual(lines[1], 'declarefloat a')
        self.assertEqual(lines[2], 'a = t0')

    def testInt2Float(self):
        lines = self._createTac('float a = 1 + 2.0;')
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], 't0 = toFloat 1')
        self.assertEqual(lines[1], 't1 = t0 + 2.0')
        self.assertEqual(lines[2], 'declarefloat a')
        self.assertEqual(lines[3], 'a = t1')

    def testPrecedence(self):
        prog = '''float a = 5 + 7.0;
        int b = 6;
        float c = a / b + (6 - 2) / 2 ^ 2;
        '''
        lines = self._createTac(prog)
        self.assertEqual(len(lines), 15)
        self.assertEqual(lines[0], 't0 = toFloat 5')
        self.assertEqual(lines[1], 't1 = t0 + 7.0')
        self.assertEqual(lines[2], 'declarefloat a')
        self.assertEqual(lines[3], 'a = t1')
        self.assertEqual(lines[4], 'declareint b')
        self.assertEqual(lines[5], 'b = 6')
        self.assertEqual(lines[6], 't2 = toFloat b')
        self.assertEqual(lines[7], 't3 = a / t2')
        self.assertEqual(lines[8], 't4 = 6 - 2')
        self.assertEqual(lines[9], 't5 = 2 ^ 2')
        self.assertEqual(lines[10], 't6 = t4 / t5')
        self.assertEqual(lines[11], 't7 = toFloat t6')
        self.assertEqual(lines[12], 't8 = t3 + t7')
        self.assertEqual(lines[13], 'declarefloat c')
        self.assertEqual(lines[14], 'c = t8')
