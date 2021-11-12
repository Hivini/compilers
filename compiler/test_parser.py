import unittest

from compiler.parser import ASTTypes, Parser


class TestParser(unittest.TestCase):

    def setUp(self):
        self.instance = Parser()
        self.parser = self.instance.createParser()

    def testPrintExp(self):
        tree = self.parser.parse('print(a);')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.PRINT)
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.VARIABLE)
        self.assertEqual(tree.children[0].children[0].value, 'a')
        self.assertEqual(self.instance.total_errors, 0)

    def testAssignInt(self):
        tree = self.parser.parse('int a = 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].value, 'a')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, 2)
        self.assertEqual(tree.children[0].children[0].children[0].type, ASTTypes.INT)
        self.assertEqual(self.instance.total_errors, 0)

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
        self.assertEqual(self.instance.total_errors, 0)

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
        self.assertEqual(self.instance.total_errors, 0)

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
        self.assertEqual(self.instance.total_errors, 0)

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
        self.assertEqual(self.instance.total_errors, 0)

    def testPrecedence(self):
        tree = self.parser.parse('int a = 4/2+2*6/4-1;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].value, 'a')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, 4)
        self.assertEqual(self.instance.total_errors, 0)

    def testIntAssignedFloat(self):
        tree = self.parser.parse('int b = 5 / 4;')
        self.assertEqual(self.instance.total_errors, 1)

    def testNoEndSentence(self):
        tree = self.parser.parse('print(a)')
        self.assertEqual(tree, None)
        self.assertEqual(self.instance.total_errors, 1)
