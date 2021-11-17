import unittest

from compiler.parser import ASTTypes, Parser, VariableTypes
from compiler.semantics import SemanticAnalyzer, SemanticError


class TestSemantics(unittest.TestCase):

    def setUp(self):
        # Just numbers as lines to avoid errors
        lines = [x for x in range(0, 20)]
        self.parser = Parser(lines)

    def _prepareSemantics(self, prog):
        root = self.parser.parseProgram(prog)
        semanticInstance = SemanticAnalyzer(root, self.parser.proglines)
        semanticInstance.checkSemantics()
        return root

    def testVariableOperation(self):
        code = '''int variable = 2;
        int variableOperation = 1 + variable;
        '''
        tree = self._prepareSemantics(code)
        self.assertEqual(len(tree.children), 2)
        self.assertEqual(tree.children[1].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[1].variableType, VariableTypes.INT)
        self.assertEqual(len(tree.children[1].children), 1)
        self.assertEqual(tree.children[1].variableValue, 3)

    def testIntegerSum(self):
        tree = self._prepareSemantics('int integerSum = 5+2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.INT)
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].variableValue, 7)

    def testFloatSum(self):
        tree = self._prepareSemantics('float floatSum = 5+2.0;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.FLOAT_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.FLOAT)
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].variableValue, 7.0)

    def testIntToFloat(self):
        tree = self._prepareSemantics('float floatSum = 5;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.FLOAT_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.FLOAT)
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].variableValue, 5)
        self.assertEqual(len(tree.children[0].children[0].children), 1)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.INT_TO_FLOAT)

    def testConcatenation(self):
        tree = self._prepareSemantics('string floatSum = "hola" + " mundo";')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.STRING_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.STRING)
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].variableValue, "hola mundo")
        self.assertEqual(len(tree.children[0].children[0].children), 1)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.SUM)

    def testConcatenationWithNums(self):
        tree = self._prepareSemantics(
            'string floatSum = "hola" + " mundo" + 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.STRING_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.STRING)
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].variableValue, "hola mundo2")
        self.assertEqual(len(tree.children[0].children[0].children), 1)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.SUM)

    def testSubstraction(self):
        tree = self._prepareSemantics('int sum = 1 - 3 + 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.INT)
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].variableValue, 0)

    def testMultiplication(self):
        tree = self._prepareSemantics('int sum = 2 * 3 + 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.INT)
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].variableValue, 8)

    def testDivision(self):
        tree = self._prepareSemantics('int div = 4 / 2 + 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.INT)
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].variableValue, 4)

    def testDivisionWithFloat(self):
        tree = self._prepareSemantics('float div = 4 / 2 + 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.FLOAT_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.FLOAT)
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].variableValue, 4.0)

    def testExponent(self):
        tree = self._prepareSemantics('float div = 4 ^ 2 + 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.FLOAT_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.FLOAT)
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].variableValue, 18)

    def testUMinus(self):
        tree = self._prepareSemantics(
            'float uminus = -((1 + 2) * 3 + 4.0 + 2^3);')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.FLOAT_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.FLOAT)
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].variableValue, -21)

    def testCmpEqual(self):
        tree = self._prepareSemantics(
            'bool cmpequal = true == "true";')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.BOOL)
        self.assertEqual(tree.children[0].variableValue, False)

    def testCmpNotEqual(self):
        tree = self._prepareSemantics(
            'bool cmpnotequal = 4 != 5;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.BOOL)
        self.assertEqual(tree.children[0].variableValue, True)

    def testCmpGreaterEqual(self):
        tree = self._prepareSemantics(
            'bool cmpgreatere = 4 >= 5;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.BOOL)
        self.assertEqual(tree.children[0].variableValue, False)

    def testCmpLessEqual(self):
        tree = self._prepareSemantics(
            'bool lesse = 4 <= 5;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.BOOL)
        self.assertEqual(tree.children[0].variableValue, True)

    def testCmpGreater(self):
        tree = self._prepareSemantics(
            'bool less = 5 > 5;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.BOOL)
        self.assertEqual(tree.children[0].variableValue, False)

    def testCmpLess(self):
        tree = self._prepareSemantics(
            'bool less = 5 < 5;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.BOOL)
        self.assertEqual(tree.children[0].variableValue, False)

    def testAndOpBools(self):
        tree = self._prepareSemantics(
            'bool andbools = true and false;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.BOOL)
        self.assertEqual(tree.children[0].variableValue, False)

    def testAndOpBoolInt(self):
        tree = self._prepareSemantics(
            'bool andbools = false and 1;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.BOOL)
        self.assertEqual(tree.children[0].variableValue, False)

    def testAndOpBoolIntZero(self):
        tree = self._prepareSemantics(
            'bool andbools = true and 0;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.BOOL)
        self.assertEqual(tree.children[0].variableValue, False)

    def testInvalidIntType(self):
        code = '''int invalidinttype = true;'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidFloatType(self):
        code = '''float invalidfloattype = true;'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidStringType(self):
        code = '''string invalidstringtype = true;'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidBoolType(self):
        code = '''bool invalidbooltype = "Hola";'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidSum(self):
        code = '''int invalidsumtype = 1 + true;'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidSubstractionBool(self):
        code = '''int invalidsumtype = 1 - true;'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidSubstractionString(self):
        code = '''int invalidsumtype = 1 - "true";'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidMultiplicationBool(self):
        code = '''int invalidsumtype = 1 * true;'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidMultiplicationString(self):
        code = '''int invalidsumtype = 1 * "true";'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidDivisionBool(self):
        code = '''int invalidsumtype = 1 / true;'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidDivisionString(self):
        code = '''int invalidsumtype = 1 / "true";'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testDivisionByZero(self):
        code = '''int invalidsumtype = 1 / 0;'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testAssignIntFloatDivision(self):
        code = '''int invalidsumtype = 1 / 0.23;'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidExponentBool(self):
        code = '''int invalidsumtype = 1 ^ true;'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidExponentString(self):
        code = '''int invalidsumtype = 1 ^ "true";'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidUminusBool(self):
        code = '''int invalidsumtype = -true;'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidUminusString(self):
        code = '''int invalidsumtype = -"true";'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidCMPEQ(self):
        code = '''bool invcmpeq = 2 == "2";'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidCMPNEQ(self):
        code = '''bool invcmpneq = 2 != "2";'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidCMPGEQString(self):
        code = '''bool invcmpgeqs = 2 >= "2";'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidCMPGEQBool(self):
        code = '''bool invcmpgeqb = 2 >= true;'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidCMPLEQString(self):
        code = '''bool invcmpleqs = 2 <= "true";'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidCMPLEQBool(self):
        code = '''bool invcmpleqb = 2 <= true;'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidCMPGString(self):
        code = '''bool invcmpgs = 2 > "2";'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidCMPGBool(self):
        code = '''bool invcmpgb = 2 > true;'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidCMPLString(self):
        code = '''bool invcmpls = 2 < "true";'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidCMPLBool(self):
        code = '''bool invcmplb = 2 < true;'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidAndOpNumNum(self):
        code = '''bool andopnumnum = 2 and 2;'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidAndOpBoolString(self):
        code = '''bool andopnumnum = true and "string";'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidAndOpIntString(self):
        code = '''bool andopnumnum = 1 and "string";'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidOrOpNumNum(self):
        code = '''bool oropnumnum = 2 or 2;'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidAndOpBoolString(self):
        code = '''bool oropnumnum = true or "string";'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)

    def testInvalidAndOpIntString(self):
        code = '''bool oropnumnum = 1 or "string";'''
        self.assertRaises(SemanticError, self._prepareSemantics, code)
