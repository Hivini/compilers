import unittest

from compiler.parser import ASTTypes, Parser, ParserError


class TestParser(unittest.TestCase):

    def setUp(self):
        self.instance = Parser()
        self.parser = self.instance.createParser()

    def testPrintExp(self):
        code = '''int printexp = 2;
        print(printexp);
        '''
        tree = self.parser.parse(code)
        self.assertEqual(len(tree.children), 2)
        self.assertEqual(tree.children[1].type, ASTTypes.PRINT)
        self.assertEqual(len(tree.children[1].children), 1)
        self.assertEqual(tree.children[1].children[0].type, ASTTypes.VARIABLE)
        self.assertEqual(tree.children[1].children[0].value, 2)

    def testAssignInt(self):
        tree = self.parser.parse('int assignInt = 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].value, 'assignInt')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, 2)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.INT)

    def testAssignFloat(self):
        tree = self.parser.parse('float assignFloat = 2.2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.FLOAT_DCL)
        self.assertEqual(tree.children[0].value, 'assignFloat')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, 2.2)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.FLOAT)

    def testAssignString(self):
        tree = self.parser.parse('string assignString = "hola";')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.STRING_DCL)
        self.assertEqual(tree.children[0].value, 'assignString')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, '"hola"')
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.STRING)

    def testAssignBooleanTrue(self):
        tree = self.parser.parse('bool assignBool = true;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].value, 'assignBool')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, True)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.BOOL_TRUE)

    def testAssignBooleanFalse(self):
        tree = self.parser.parse('bool assignBoolF = false;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].value, 'assignBoolF')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, False)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.BOOL_FALSE)

    def testAssignSum(self):
        tree = self.parser.parse('int sum = 2 + 3;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].value, 'sum')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, 5)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.SUM)
        self.assertEqual(
            len(tree.children[0].children[0].children[0].children), 2)

    def testAssignSubstract(self):
        tree = self.parser.parse('int substract = 2 - 3;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].value, 'substract')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, -1)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.SUBSTRACT)
        self.assertEqual(
            len(tree.children[0].children[0].children[0].children), 2)

    def testAssignMultiplication(self):
        tree = self.parser.parse('int multiplication = 2 * 3;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].value, 'multiplication')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, 6)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.MULTIPLICATION)
        self.assertEqual(
            len(tree.children[0].children[0].children[0].children), 2)

    def testAssignDivision(self):
        tree = self.parser.parse('int div = 4/2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].value, 'div')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, 2)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.DIVISION)
        self.assertEqual(
            len(tree.children[0].children[0].children[0].children), 2)

    def testAssignExponent(self):
        tree = self.parser.parse('int exp = 2^6;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].value, 'exp')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, 64)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.EXPONENT)
        self.assertEqual(
            len(tree.children[0].children[0].children[0].children), 2)

    def testUminus(self):
        tree = self.parser.parse('int uminus = -((3 + 3) / 2 * (2+2));')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].value, 'uminus')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, -12)

    def testPrecedence(self):
        tree = self.parser.parse('int precedence = 4/2^2+2*6/4-1;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].value, 'precedence')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, 3)

    def testIntAssignedFloat(self):
        self.assertRaises(ParserError, self.parser.parse, 'int invfloatint = 5 / 4;')

    def testDivisionByZero(self):
        self.assertRaises(ParserError, self.parser.parse, 'float divZero = 30 / (2*3 - 6);')

    def testExistingVariableDeclaration(self):
        code = '''int existing = 1;
        int existing = 2;
        '''
        self.assertRaises(ParserError, self.parser.parse, code)

    def testNoEndSentence(self):
        code = '''int noEnd = 2;
        print(noEnd)'''
        self.assertRaises(ParserError, self.parser.parse, code)
