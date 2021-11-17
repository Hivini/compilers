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

    def testIntSumTac(self):
        lines = self._createTac('int a = 5 + 3 + 2;')
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], 't0 = 5 + 3')
        self.assertEqual(lines[1], 't1 = t0 + 2')
        self.assertEqual(lines[2], 'int a = t1')
