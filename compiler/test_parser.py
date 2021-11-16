import unittest

from compiler.parser_2 import ASTTypes, Parser, ParserError, VariableTypes


class TestParser(unittest.TestCase):

    def setUp(self):
        # Just numbers as lines to avoid errors
        lines = [x for x in range(0, 20)]
        self.instance = Parser(lines)

    def testPrintExp(self):
        code = '''int printexp = 2;
        print(printexp);
        '''
        tree = self.instance.parseProgram(code)
        self.assertEqual(len(tree.children), 2)
        self.assertEqual(tree.children[1].type, ASTTypes.PRINT)
        self.assertEqual(len(tree.children[1].children), 1)
        self.assertEqual(tree.children[1].children[0].type, ASTTypes.VARIABLE)

    def testAssignInt(self):
        tree = self.instance.parseProgram('int assignInt = 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].variableName, 'assignInt')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.INT)
        self.assertEqual(
            tree.children[0].children[0].children[0].variableType, VariableTypes.INT)

    def testAssignFloat(self):
        tree = self.instance.parseProgram('float assignFloat = 2.2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.FLOAT_DCL)
        self.assertEqual(tree.children[0].variableName, 'assignFloat')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.FLOAT)
        self.assertEqual(
            tree.children[0].children[0].children[0].variableType, VariableTypes.FLOAT)

    def testAssignString(self):
        tree = self.instance.parseProgram('string assignString = "hola";')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.STRING_DCL)
        self.assertEqual(tree.children[0].variableName, 'assignString')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.STRING)
        self.assertEqual(
            tree.children[0].children[0].children[0].variableType, VariableTypes.STRING)

    def testAssignBooleanTrue(self):
        tree = self.instance.parseProgram('bool assignBool = true;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].variableName, 'assignBool')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.BOOL_TRUE)
        self.assertEqual(
            tree.children[0].children[0].children[0].variableType, VariableTypes.BOOL)

    def testAssignBooleanFalse(self):
        tree = self.instance.parseProgram('bool assignBoolF = false;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].variableName, 'assignBoolF')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.BOOL_FALSE)
        self.assertEqual(
            tree.children[0].children[0].children[0].variableType, VariableTypes.BOOL)

    def testAssignSum(self):
        tree = self.instance.parseProgram('int sum = 2 + 3;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].variableName, 'sum')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.SUM)
        self.assertEqual(
            len(tree.children[0].children[0].children[0].children), 2)

    def testAssignSubstract(self):
        tree = self.instance.parseProgram('int substract = 2 - 3;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].variableName, 'substract')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.SUBSTRACT)
        self.assertEqual(
            len(tree.children[0].children[0].children[0].children), 2)

    def testAssignMultiplication(self):
        tree = self.instance.parseProgram('int multiplication = 2 * 3;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].variableName, 'multiplication')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.MULTIPLICATION)
        self.assertEqual(
            len(tree.children[0].children[0].children[0].children), 2)

    def testAssignDivision(self):
        tree = self.instance.parseProgram('int div = 4/2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].variableName, 'div')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.DIVISION)
        self.assertEqual(
            len(tree.children[0].children[0].children[0].children), 2)

    def testAssignExponent(self):
        tree = self.instance.parseProgram('int exp = 2^6;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].variableName, 'exp')
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.ASSIGN)
        self.assertEqual(
            tree.children[0].children[0].children[0].type, ASTTypes.EXPONENT)
        self.assertEqual(
            len(tree.children[0].children[0].children[0].children), 2)

    def testUminus(self):
        tree = self.instance.parseProgram(
            'int uminus = -((3 + 3) / 2 * (2+2));')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(len(tree.children[0].children), 1)
        assign = tree.children[0].children[0]
        self.assertEqual(assign.type, ASTTypes.ASSIGN)
        self.assertEqual(assign.children[0].type, ASTTypes.UMINUS)

    def testCmpEqual(self):
        tree = self.instance.parseProgram('bool cmpequal = 1 == 1;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].variableName, 'cmpequal')
        self.assertEqual(len(tree.children[0].children), 1)
        assign = tree.children[0].children[0]
        self.assertEqual(assign.type, ASTTypes.ASSIGN)
        self.assertEqual(assign.children[0].type, ASTTypes.CMP_EQUAL)

    def testCmpNotEqual(self):
        tree = self.instance.parseProgram('bool cmpnotequal = 1 != 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].variableName, 'cmpnotequal')
        self.assertEqual(len(tree.children[0].children), 1)
        assign = tree.children[0].children[0]
        self.assertEqual(assign.type, ASTTypes.ASSIGN)
        self.assertEqual(assign.children[0].type, ASTTypes.CMP_NOT_EQUAL)

    def testCmpGreaterEqual(self):
        tree = self.instance.parseProgram('bool cmpgreaterequal = 2 >= 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].variableName, 'cmpgreaterequal')
        self.assertEqual(len(tree.children[0].children), 1)
        assign = tree.children[0].children[0]
        self.assertEqual(assign.type, ASTTypes.ASSIGN)
        self.assertEqual(assign.children[0].type, ASTTypes.CMP_GREATER_EQUAL)

    def testCmpLessEqual(self):
        tree = self.instance.parseProgram('bool cmplessequal = 1 <= 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].variableName, 'cmplessequal')
        self.assertEqual(len(tree.children[0].children), 1)
        assign = tree.children[0].children[0]
        self.assertEqual(assign.type, ASTTypes.ASSIGN)
        self.assertEqual(assign.children[0].type, ASTTypes.CMP_LESS_EQUAL)

    def testCmpGreater(self):
        tree = self.instance.parseProgram('bool cmpgreater = 2 > 1;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].variableName, 'cmpgreater')
        self.assertEqual(len(tree.children[0].children), 1)
        assign = tree.children[0].children[0]
        self.assertEqual(assign.type, ASTTypes.ASSIGN)
        self.assertEqual(assign.children[0].type, ASTTypes.CMP_GREATER)

    def testCmpLess(self):
        tree = self.instance.parseProgram('bool cmpless = 1 < 2;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].variableName, 'cmpless')
        self.assertEqual(len(tree.children[0].children), 1)
        assign = tree.children[0].children[0]
        self.assertEqual(assign.type, ASTTypes.ASSIGN)
        self.assertEqual(assign.children[0].type, ASTTypes.CMP_LESS)

    def testAndOperator(self):
        tree = self.instance.parseProgram('bool andop = true and false;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].variableName, 'andop')
        self.assertEqual(len(tree.children[0].children), 1)
        assign = tree.children[0].children[0]
        self.assertEqual(assign.type, ASTTypes.ASSIGN)
        self.assertEqual(assign.children[0].type, ASTTypes.AND_OP)

    def testOrOperator(self):
        tree = self.instance.parseProgram('bool orop = true or false;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.BOOL_DCL)
        self.assertEqual(tree.children[0].variableName, 'orop')
        self.assertEqual(len(tree.children[0].children), 1)
        assign = tree.children[0].children[0]
        self.assertEqual(assign.type, ASTTypes.ASSIGN)
        self.assertEqual(assign.children[0].type, ASTTypes.OR_OP)

    def testPrecedence(self):
        tree = self.instance.parseProgram('int precedence = 4/2^2+2*6/4-1;')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.INT_DCL)
        self.assertEqual(tree.children[0].variableName, 'precedence')
        self.assertEqual(len(tree.children[0].children), 1)
        assign = tree.children[0].children[0]
        self.assertEqual(assign.type, ASTTypes.ASSIGN)
        self.assertEqual(assign.children[0].type, ASTTypes.SUBSTRACT)

    def testIfStatement(self):
        prog = '''if (5 == 5) {
            int ifstatement1 = 5;
        } elif (4 == 5) {
            int elifstatement1 = 7;
        } else {
            int elsestatement1 = 8;
        }
        '''
        tree = self.instance.parseProgram(prog)
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.IF_STATEMENT)
        self.assertEqual(len(tree.children[0].children), 3)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.IF)
        self.assertEqual(tree.children[0].children[1].type, ASTTypes.ELIF)
        self.assertEqual(tree.children[0].children[2].type, ASTTypes.ELSE)
        self.assertEqual(tree.children[0].children[0].children[1].type, ASTTypes.BLOCK)
        self.assertEqual(tree.children[0].children[1].children[1].type, ASTTypes.BLOCK)
        self.assertEqual(tree.children[0].children[2].children[0].type, ASTTypes.BLOCK)

    def testWhileStatement(self):
        prog = '''while (true) {
            int a = 5;
        }
        '''
        tree = self.instance.parseProgram(prog)
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.WHILE_STATEMENT)
        self.assertEqual(len(tree.children[0].children), 2)
        self.assertEqual(tree.children[0].children[1].type, ASTTypes.BLOCK)

    def testNoEndSentence(self):
        code = '''int noEnd = 2;
        print(noEnd)'''
        self.assertRaises(ParserError, self.instance.parseProgram, code)
