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

    def testIfStatement(self):
        prog = '''
        int a = 5;
        if (2 == 2) {
            print(1);
        } 
        elif (3 >= 3 and 4 == 4) {
            print(3);
        }
        elif (a) {
            print(4);
        }
        elif (a == true) {
            a = 5;
            print(a);
        }
        else {
            print(2);
            int c = 2;
        }
        print(a);
        '''
        lines = self._createTac(prog)
        expectedLines = '''declareint a
        a = 5
        t0 = 2 == 2
        t6 = not t0
        t6 IFGOTO L0
        print 1
        GOTO L4
        LABEL L0
        t1 = 3 >= 3
        t2 = 4 == 4
        t3 = t1 and t2
        t7 = not t3
        t7 IFGOTO L1
        print 3
        GOTO L4
        LABEL L1
        t4 = a
        t8 = not t4
        t8 IFGOTO L2
        print 4
        GOTO L4
        LABEL L2
        t5 = a == True
        t9 = not t5
        t9 IFGOTO L3
        a = 5
        print a
        GOTO L4
        LABEL L3
        print 2
        declareint c
        c = 2
        LABEL L4
        print a
        '''
        expectedLines = expectedLines.split('\n')
        for i in range(len(expectedLines)):
            expectedLines[i] = expectedLines[i].strip()
        self.assertEqual(len(lines), 34)
        for i in range(len(lines)):
            self.assertEqual(lines[i], expectedLines[i])

    def testWhileStatement(self):
        prog = '''
        bool a = true;
        int i = 0;
        while (a) {
            print(a);
            if (i == 10) {
                a = false;
            }
            i = i + 1;
        }
        '''
        lines = self._createTac(prog)
        expectedLines = '''declarebool a
        a = True
        declareint i
        i = 0
        LABEL L0
        t3 = not a
        t3 IFGOTO L2
        print a
        t0 = i == 10
        t1 = not t0
        t1 IFGOTO L1
        a = False
        LABEL L1
        t2 = i + 1
        i = t2
        GOTO L0
        LABEL L2
        '''
        expectedLines = expectedLines.split('\n')
        for i in range(len(expectedLines)):
            expectedLines[i] = expectedLines[i].strip()
        self.assertEqual(len(lines), 17)
        for i in range(len(lines)):
            self.assertEqual(lines[i], expectedLines[i])

    def testForStatement(self):
        prog = '''
        for (int i = 0; i < 9; i = i+1) {
            int a = 5;
            print(a);
        }
        int i = 2;
        '''
        lines = self._createTac(prog)
        expectedLines = '''declareint i
        i = 0
        LABEL L0
        t0 = i < 9
        t2 = not t0
        t2 IFGOTO L1
        declareint a
        a = 5
        print a
        t1 = i + 1
        i = t1
        GOTO L0
        LABEL L1
        declareint i
        i = 2
        '''
        expectedLines = expectedLines.split('\n')
        for i in range(len(expectedLines)):
            expectedLines[i] = expectedLines[i].strip()
        self.assertEqual(len(lines), 15)
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
