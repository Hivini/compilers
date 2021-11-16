import unittest

from compiler.parser import ASTTypes, Parser, ParserError, VariableTypes
from compiler.semantics import SemanticAnalyzer, SemanticError


class TestParser(unittest.TestCase):

    def setUp(self):
        # Just numbers as lines to avoid errors
        lines = [x for x in range(0, 20)]
        self.parser = Parser(lines)
    
    def _prepareSemantics(self, prog):
        root = self.parser.parseProgram(prog)
        semanticInstance = SemanticAnalyzer(root, self.parser.proglines)
        semanticInstance.checkSemantics()
        return root

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
        self.assertEqual(tree.children[0].children[0].children[0].type, ASTTypes.INT_TO_FLOAT)

    def testConcatenation(self):
        tree = self._prepareSemantics('string floatSum = "hola" + " mundo";')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.STRING_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.STRING)
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].variableValue, "hola mundo")
        self.assertEqual(len(tree.children[0].children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].children[0].type, ASTTypes.CONCATENATION)

    def testConcatenationWithNums(self):
        tree = self._prepareSemantics('string floatSum = "hola" + " mundo" + 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.STRING_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.STRING)
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].variableValue, "hola mundo2")
        self.assertEqual(len(tree.children[0].children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].children[0].type, ASTTypes.CONCATENATION)

    def testSubstraction(self):
        tree = self._prepareSemantics('int sum = 1 - 3 + 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].variableType, VariableTypes.INT)
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].variableValue, 0)

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