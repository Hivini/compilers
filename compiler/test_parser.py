import unittest

from compiler.parser import ASTTypes, Parser, ParserError


class TestParser(unittest.TestCase):

    def setUp(self):
        self.instance = Parser()
        self.parser = self.instance.createParser()

    def testPrintExp(self):
        code = '''int a = 2;
        print(a);
        '''
        tree = self.parser.parse(code)
        self.assertEqual(len(tree.children), 2)
        self.assertEqual(tree.children[1].type, ASTTypes.PRINT)
        self.assertEqual(len(tree.children[1].children), 1)
        self.assertEqual(tree.children[1].children[0].type, ASTTypes.VARIABLE)
        self.assertEqual(tree.children[1].children[0].value, 2)

    def testAssignInt(self):
        tree = self.parser.parse('int a = 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].value, 'a')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, 2)
        self.assertEqual(tree.children[0].children[0].children[0].type, ASTTypes.INT)

    def testAssignFloat(self):
        tree = self.parser.parse('float a = 2.2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.FLOAT_DCL)
        self.assertEqual(tree.children[0].value, 'a')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, 2.2)
        self.assertEqual(tree.children[0].children[0].children[0].type, ASTTypes.FLOAT)

    def testAssignSum(self):
        tree = self.parser.parse('int a = 2 + 3;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].value, 'a')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, 5)
        self.assertEqual(tree.children[0].children[0].children[0].type, ASTTypes.SUM)
        self.assertEqual(len(tree.children[0].children[0].children[0].children), 2)

    def testAssignSubstract(self):
        tree = self.parser.parse('int a = 2 - 3;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].value, 'a')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, -1)
        self.assertEqual(tree.children[0].children[0].children[0].type, ASTTypes.SUBSTRACT)
        self.assertEqual(len(tree.children[0].children[0].children[0].children), 2)

    def testAssignMultiplication(self):
        tree = self.parser.parse('int a = 2 * 3;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].value, 'a')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, 6)
        self.assertEqual(tree.children[0].children[0].children[0].type, ASTTypes.MULTIPLICATION)
        self.assertEqual(len(tree.children[0].children[0].children[0].children), 2)

    def testAssignDivision(self):
        tree = self.parser.parse('int a = 4/2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].value, 'a')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, 2)
        self.assertEqual(tree.children[0].children[0].children[0].type, ASTTypes.DIVISION)
        self.assertEqual(len(tree.children[0].children[0].children[0].children), 2)

    def testUminus(self):
        tree = self.parser.parse('int a = -((3 + 3) / 2 * (2+2));')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].value, 'a')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, -12)

    def testPrecedence(self):
        tree = self.parser.parse('int a = 4/2+2*6/4-1;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].value, 'a')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, 4)

    def testIntAssignedFloat(self):
        self.assertRaises(ParserError, self.parser.parse, 'int b = 5 / 4;')

    def testNoEndSentence(self):
        code = '''int a = 2;
        print(a)'''
        self.assertRaises(ParserError, self.parser.parse, code)
