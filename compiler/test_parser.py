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

    def testAssignFloatWithInt(self):
        tree = self.parser.parse('float floatasInt = 4;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.FLOAT_DCL)
        self.assertEqual(tree.children[0].value, 'floatasInt')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, 4)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.INT)

    def testAssignString(self):
        tree = self.parser.parse('string assignString = "hola";')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.STRING_DCL)
        self.assertEqual(tree.children[0].value, 'assignString')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, 'hola')
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

    def testCmpEqual(self):
        tree = self.parser.parse('bool cmpequal = 1 == 1;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].value, 'cmpequal')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, True)

    def testCmpNotEqual(self):
        tree = self.parser.parse('bool cmpnotequal = 1 != 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].value, 'cmpnotequal')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, True)

    def testCmpGreaterEqual(self):
        tree = self.parser.parse('bool cmpgreaterequal = 2 >= 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].value, 'cmpgreaterequal')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, True)

    def testCmpLessEqual(self):
        tree = self.parser.parse('bool cmplessequal = 1 <= 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].value, 'cmplessequal')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, True)

    def testCmpGreater(self):
        tree = self.parser.parse('bool cmpgreater = 2 > 1;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].value, 'cmpgreater')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, True)

    def testCmpLess(self):
        tree = self.parser.parse('bool cmpless = 1 < 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].value, 'cmpless')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, True)

    def testAndOperator(self):
        tree = self.parser.parse('bool andop = true and false;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].value, 'andop')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, False)

    def testOrOperator(self):
        tree = self.parser.parse('bool orop = true or false;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].value, 'orop')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, True)

    def testPrecedence(self):
        tree = self.parser.parse('int precedence = 4/2^2+2*6/4-1;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].value, 'precedence')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, 3)

    def testConcatenationStrs(self):
        tree = self.parser.parse('string concstr = "hola" + "mundo";')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.STRING_DCL)
        self.assertEqual(tree.children[0].value, 'concstr')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, "holamundo")

    def testConcatenationNums(self):
        tree = self.parser.parse('string concnums = "hola" + 1 + "" + 23;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.STRING_DCL)
        self.assertEqual(tree.children[0].value, 'concnums')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(tree.children[0].children[0].value, "hola123")

    def testIntAssignedFloat(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'int invfloatint = 5 / 4;')

    def testIntWrongType(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'int wrongInt = "hola";')

    def testFloatWrongType(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'float wrongFloat = "hola";')

    def testStringWrongType(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'string wrongString = 2;')

    def testBooleanWrongType(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'bool wrongbool = 2;')

    def testWrongSum(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'int wrongsumbool = 3 + true;')

    def testWrongSubstractStr(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'int wrongminustr = 3 - "hola";')

    def testWrongSubstractStr(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'int wrongminusbool = 3 - true;')

    def testWrongMultiplyStr(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'int wrongstrmult = 3 * "hola";')

    def testWrongMultiplyBool(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'int wrongboolmult = 3 * true;')

    def testWrongDivisionStr(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'int wrongstrdiv = 3 / "hola";')

    def testWrongDivisionBool(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'int wrongbooldiv = 3 / true;')

    def testDivisionByZero(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'float divZero = 30 / (2*3 - 6);')

    def testWrongExpStr(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'int wrongstrexp = 3^"hola";')

    def testWrongExpBool(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'int wrongboolexp = 3^true;')

    def testEqualInvalid(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'bool equalInvalid = 3 == "hola";')

    def testUnequalInvalid(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'bool unequalInvalid = 3 != "hola";')

    def testGreaterEqualInvalidStr(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'bool greaterEqualInvalidStr = 3 >= "hola";')

    def testGreaterEqualInvalidBool(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'bool greaterEqualInvalidBool = 3 >= true;')

    def testLessEqualInvalidStr(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'bool lessEqualInvalidStr = 3 <= "hola";')

    def testLessEqualInvalidBool(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'bool lessEqualInvalidBool = 3 <= true;')

    def testGreaterInvalidStr(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'bool greaterInvalidStr = 3 > "hola";')

    def testGreaterInvalidBool(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'bool greaterInvalidBool = 3 > true;')

    def testLessInvalidStr(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'bool lessInvalidStr = 3 < "hola";')

    def testLessInvalidBool(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'bool lessInvalidBool = 3 < true;')

    def testInvalidOperatorAnd(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'bool invalidAnd = 3 and true;')

    def testInvalidOperatorOr(self):
        self.assertRaises(ParserError, self.parser.parse,
                          'bool invalidOr = 3 or true;')

    def testExistingVariableDeclaration(self):
        code = '''int existing = 1;
        int existing = 2;
        '''
        self.assertRaises(ParserError, self.parser.parse, code)

    def testNoEndSentence(self):
        code = '''int noEnd = 2;
        print(noEnd)'''
        self.assertRaises(ParserError, self.parser.parse, code)
