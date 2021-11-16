import ply.yacc as yacc

from compiler.lexer import Lexer
from enum import Enum
from typing import List


class ParserError(Exception):
    pass


class VariableTypes(Enum):
    INT = 1
    FLOAT = 2
    STRING = 3
    BOOL = 4


class Variable:
    def __init__(self, type: VariableTypes, value: any) -> None:
        self.type = type
        self.value = value

    def __str__(self) -> str:
        return f'| Type: {self.type}, Value: {self.value} |'

    def __repr__(self) -> str:
        return f'| Type: {self.type}, Value: {self.value} |'


class ASTTypes(Enum):
    BLOCK = 0
    PRINT = 1
    VARIABLE = 2
    ASSIGN = 3
    INT = 4
    INT_DCL = 5
    FLOAT = 6
    FLOAT_DCL = 7
    STRING = 8
    STRING_DCL = 9
    BOOL_TRUE = 10
    BOOL_FALSE = 11
    BOOL_DCL = 12
    CMP_EQUAL = 14
    CMP_NOT_EQUAL = 15
    CMP_GREATER_EQUAL = 16
    CMP_LESS_EQUAL = 17
    CMP_GREATER = 18
    CMP_LESS = 19
    AND_OP = 20
    OR_OP = 21
    IF = 22
    ELIF = 23
    ELSE = 24
    IF_STATEMENT = 25
    INT_TO_FLOAT = 26
    SUM = 50
    SUBSTRACT = 51
    MULTIPLICATION = 52
    DIVISION = 53
    UMINUS = 54
    EXPONENT = 55
    CONCATENATION = 56


class ASTNode:
    def __init__(self, type: ASTTypes, children: List[any] = None,
                 variableType: VariableTypes = None, variableValue: any = None,
                 variableName: str = None):
        self.type = type
        if children:
            self.children = children
        else:
            self.children = []
        self.variableType = variableType
        self.variableValue = variableValue
        self.variableName = variableName

    def __str__(self) -> str:
        return f'{self.type.name}'


class Parser:
    precedence = (
        ('left', 'AND_OP', 'OR_OP'),
        ('left', 'EQUALS', 'NOT_EQUAL'),
        ('nonassoc', '<', '>', 'GREATER_EQUAL', 'LESS_EQUAL'),
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('left', '^'),
        ('right', 'UMINUS'),
    )

    names = {}

    def __init__(self, proglines) -> None:
        self.lexerInstance = Lexer()
        self.lexer = self.lexerInstance.createLexer()
        self.tokens = self.lexerInstance.tokens
        self.start = 'program'
        self.first_error = ''
        self.proglines = proglines

    def _addError(self, error: str, lineNumber: int = None):
        if lineNumber:
            error = f'{error}:\n\t{lineNumber})\t{self.proglines[lineNumber-1]}'
        self.first_error = error
        raise ParserError('Parser Error!')

    def p_program(self, p):
        '''program : expression program
                    | expression
        '''
        if len(p) == 3:
            children = [p[1]]
            children.extend(p[2].children)
            p[0] = ASTNode(ASTTypes.BLOCK, children)
        else:
            p[0] = ASTNode(ASTTypes.BLOCK, [p[1]])

    def p_line(self, p):
        '''expression : statement SENTENCE_END
        '''
        p[0] = p[1]

    def p_statement_declare_int(self, p):
        '''statement : INTDCL NAME assignment
        '''
        if p[3].variableType != VariableTypes.INT:
            self._addError('Value cannot be assigned to int.', p.lineno(2))
        tmp = ASTNode(ASTTypes.INT_DCL, children=[
                      p[3]], variableType=p[3].variableType, variableValue=p[2])
        self._addToNames(p[2], VariableTypes.INT, p[3].variableValue)
        p[0] = tmp

    def p_statement_declare_float(self, p):
        '''statement : FLOATDCL NAME assignment
        '''
        if p[3].variableType == VariableTypes.INT:
            c = []
            c.extend(p[3].children)
            p[3].children = [
                ASTNode(ASTTypes.INT_TO_FLOAT, children=c, variableType=VariableTypes.FLOAT)]
            p[3].variableType = VariableTypes.FLOAT
        elif p[3].variableType != VariableTypes.FLOAT:
            self._addError(
                'Value cannot be assigned to float.', p.lineno(2))
        tmp = ASTNode(ASTTypes.FLOAT_DCL, children=[
                      p[3]], variableType=p[3].variableType, variableValue=p[2])
        self._addToNames(p[2], VariableTypes.FLOAT, p[3].variableValue)
        p[0] = tmp

    def p_statement_declare_string(self, p):
        '''statement : STRING_DCL NAME assignment
        '''
        if p[3].variableType != VariableTypes.STRING:
            self._addError(
                'Value cannot be assigned to string', p.lineno(2))
        tmp = ASTNode(ASTTypes.STRING_DCL, children=[
                      p[3]], variableType=p[3].variableType, variableValue=p[2])
        self._addToNames(p[2], VariableTypes.STRING, p[3].variableValue)
        p[0] = tmp

    def p_statement_declare_boolean(self, p):
        '''statement : BOOL_DCL NAME assignment
        '''
        if p[3].variableType != VariableTypes.BOOL:
            self._addError(
                'Value cannot be assigned to boolean', p.lineno(2))
        tmp = ASTNode(ASTTypes.BOOL_DCL, children=[
                      p[3]], variableType=p[3].variableType, variableValue=p[2])
        self._addToNames(p[2], VariableTypes.BOOL, p[3].variableValue)
        p[0] = tmp

    def p_assignment(self, p):
        '''assignment : '=' declaration '''
        p[0] = ASTNode(ASTTypes.ASSIGN, children=[p[2]],
                       variableType=p[2].variableType, variableValue=p[2].variableValue)

    def p_expression_print(self, p):
        '''statement : PRINT '(' declaration ')' '''
        p[0] = ASTNode(ASTTypes.PRINT, [p[3]])

    def p_expression_binop(self, p):
        '''declaration : declaration '+' declaration
                    | declaration '-' declaration
                    | declaration '*' declaration
                    | declaration '/' declaration
                    | declaration '^' declaration
        '''
        leftT = p[1].variableType
        rightT = p[3].variableType
        leftV = p[1].variableValue
        rightV = p[3].variableValue
        op = p[2]
        self._checkArithmeticOperation(
            leftT, rightT, leftV, rightV, op, p.lineno(2))
        if op == '+':
            if leftT == VariableTypes.STRING or rightT == VariableTypes.STRING:
                p[0] = ASTNode(ASTTypes.CONCATENATION, children=[
                               p[1], p[3]], variableType=VariableTypes.STRING, variableValue=str(leftV) + str(rightV))
            elif leftT == VariableTypes.FLOAT or rightT == VariableTypes.FLOAT:
                p[0] = ASTNode(
                    ASTTypes.SUM, variableType=VariableTypes.FLOAT, children=[p[1], p[3]], variableValue=leftV + rightV)
            else:
                p[0] = ASTNode(
                    ASTTypes.SUM, variableType=VariableTypes.INT, children=[p[1], p[3]], variableValue=leftV + rightV)
        elif op == '-':
            if leftT == VariableTypes.FLOAT or rightT == VariableTypes.FLOAT:
                p[0] = ASTNode(
                    ASTTypes.SUBSTRACT, variableType=VariableTypes.FLOAT, children=[p[1], p[3]], variableValue=leftV - rightV)
            else:
                p[0] = ASTNode(
                    ASTTypes.SUBSTRACT, variableType=VariableTypes.INT, children=[p[1], p[3]], variableValue=leftV - rightV)
        elif op == '*':
            if leftT == VariableTypes.FLOAT or rightT == VariableTypes.FLOAT:
                p[0] = ASTNode(
                    ASTTypes.MULTIPLICATION, variableType=VariableTypes.FLOAT, children=[p[1], p[3]], variableValue=leftV * rightV)
            else:
                p[0] = ASTNode(
                    ASTTypes.MULTIPLICATION, variableType=VariableTypes.INT, children=[p[1], p[3]], variableValue=leftV * rightV)
        elif op == '/':
            val = leftV / rightV
            typeVal = VariableTypes.FLOAT
            if leftT == VariableTypes.FLOAT or rightT == VariableTypes.FLOAT:
                p[0] = ASTNode(ASTTypes.DIVISION, variableType=typeVal,
                               variableValue=val, children=[p[1], p[3]])
            else:
                if val.is_integer():
                    typeVal = VariableTypes.INT
                    val = int(val)
                p[0] = ASTNode(ASTTypes.DIVISION, variableType=typeVal,
                               variableValue=val, children=[p[1], p[3]])
        elif op == '^':
            if leftT == VariableTypes.FLOAT or rightT == VariableTypes.FLOAT or rightV < 0:
                p[0] = ASTNode(ASTTypes.EXPONENT, variableType=VariableTypes.FLOAT, variableValue=pow(
                    leftV, rightV), children=[p[1], p[3]])
            else:
                p[0] = ASTNode(ASTTypes.EXPONENT, variableType=VariableTypes.INT, variableValue=pow(
                    leftV, rightV), children=[p[1], p[3]])

    def p_expression_cmpop(self, p):
        '''declaration : declaration EQUALS declaration
                    | declaration NOT_EQUAL declaration
                    | declaration GREATER_EQUAL declaration
                    | declaration LESS_EQUAL declaration
                    | declaration '>' declaration
                    | declaration '<' declaration
        '''
        leftT = p[1].variableType
        rightT = p[3].variableType
        leftV = p[1].variableValue
        rightV = p[3].variableValue
        op = p[2]
        self._checkComparisonOperation(
            leftT, rightT, leftV, rightV, op, p.lineno(2))
        if op == '==':
            p[0] = ASTNode(ASTTypes.CMP_EQUAL, variableType=VariableTypes.BOOL, variableValue=leftV ==
                           rightV, children=[p[1], p[3]])
        elif op == '!=':
            p[0] = ASTNode(ASTTypes.CMP_NOT_EQUAL, variableType=VariableTypes.BOOL, variableValue=leftV !=
                           rightV, children=[p[1], p[3]])
        elif op == '>=':
            p[0] = ASTNode(ASTTypes.CMP_GREATER_EQUAL, variableType=VariableTypes.BOOL, variableValue=leftV >=
                           rightV, children=[p[1], p[3]])
        elif p[2] == '<=':
            p[0] = ASTNode(ASTTypes.CMP_LESS_EQUAL, variableType=VariableTypes.BOOL, variableValue=leftV <=
                           rightV, children=[p[1], p[3]])
        elif p[2] == '>':
            p[0] = ASTNode(ASTTypes.CMP_GREATER, variableType=VariableTypes.BOOL, variableValue=leftV >
                           rightV, children=[p[1], p[3]])
        elif p[2] == '<':
            p[0] = ASTNode(ASTTypes.CMP_LESS, variableType=VariableTypes.BOOL, variableValue=leftV <
                           rightV, children=[p[1], p[3]])

    def p_expression_boolop(self, p):
        '''declaration : declaration AND_OP declaration
                    | declaration OR_OP declaration
        '''
        leftT = p[1].variableType
        rightT = p[3].variableType
        leftV = p[1].variableValue
        rightV = p[3].variableValue
        print(leftV)
        print(rightV)
        self._checkBoolOperator(leftT, rightT, leftV, rightV, p.lineno(2))
        if p[2] == 'and':
            p[0] = ASTNode(ASTTypes.AND_OP, variableType=VariableTypes.BOOL,
                           variableValue=leftV and rightV, children=[p[1], p[3]])
        elif p[2] == 'or':
            p[0] = ASTNode(ASTTypes.OR_OP, variableType=VariableTypes.BOOL,
                           variableValue=leftV or rightV, children=[p[1], p[3]])

    def p_expression_group(self, p):
        '''declaration : '(' declaration ')' '''
        p[0] = p[2]

    def p_expression_uminus(self, t):
        '''declaration : - declaration %prec UMINUS'''
        t[0] = ASTNode(ASTTypes.UMINUS, value=-t[2].value, children=[t[2]])

    def p_expression_intnum(self, p):
        '''declaration : INTNUM '''
        p[0] = ASTNode(
            ASTTypes.INT, variableType=VariableTypes.INT, variableValue=p[1])

    def p_expression_floatnum(self, p):
        '''declaration : FLOATNUM '''
        p[0] = ASTNode(
            ASTTypes.FLOAT, variableType=VariableTypes.FLOAT, variableValue=p[1])

    def p_expression_bool_true(self, p):
        '''declaration : BOOL_TRUE '''
        p[0] = ASTNode(ASTTypes.BOOL_TRUE,
                       variableType=VariableTypes.BOOL, variableValue=p[1])

    def p_expression_bool_false(self, p):
        '''declaration : BOOL_FALSE '''
        p[0] = ASTNode(ASTTypes.BOOL_FALSE,
                       variableType=VariableTypes.BOOL, variableValue=p[1])

    def p_expression_string(self, p):
        '''declaration : STRING '''
        p[0] = ASTNode(ASTTypes.STRING,
                       variableType=VariableTypes.STRING, variableValue=p[1].replace('"', ''))

    def p_expression_name(self, p):
        '''declaration : NAME '''
        if (p[1] in self.names):
            p[0] = ASTNode(
                ASTTypes.VARIABLE, variableType=self.names[p[1]].type, variableValue=self.names[p[1]].value, variableName=p[1])
        else:
            self._addError(f'Variable {p[1]} does not exist', p.lineno(1))

    def p_error(self, p):
        if p:
            self._addError(
                f'Unexpected symbol "{p.value}", at line {p.lineno}', p.lineno)
        self._addError('Unexpected end of file reached')

    def _checkArithmeticOperation(self, leftT, rightT, leftValue, rightValue, operation: str, lineno: int):
        numTypes = [VariableTypes.INT, VariableTypes.FLOAT]
        bothAreNums = leftT in numTypes and rightT in numTypes
        if operation == '+':
            if leftT == VariableTypes.BOOL or rightT == VariableTypes.BOOL:
                self._addError(
                    f'Cannot sum values "{leftValue}" and "{rightValue}"', lineno)
        elif operation == '-':
            if not(bothAreNums):
                self._addError(
                    f'Cannot substract values "{leftValue}" and "{rightValue}"', lineno)
        elif operation == '*':
            if not(bothAreNums):
                self._addError(
                    f'Cannot multiply values "{leftValue}" and "{rightValue}"', lineno)
        elif operation == '/':
            if not(bothAreNums):
                self._addError(
                    f'Cannot divide values "{leftValue}" and "{rightValue}"', lineno)
            elif rightValue == 0:
                self._addError(
                    f'{leftValue} / {rightValue} is invalid. Cannot perform division by zero.', lineno)
        elif operation == '^':
            if not(bothAreNums):
                self._addError(
                    f'Cannot get the exponent of "{leftValue}" ^ "{rightValue}"', lineno)

    def _checkComparisonOperation(self, leftType, rightType, leftValue, rightValue, operation: str, lineno: int):
        numTypes = [VariableTypes.INT, VariableTypes.FLOAT]
        tl = leftType
        tr = rightType
        areNumAndStrings = (tl in numTypes and tr == VariableTypes.STRING) or (
            tr in numTypes and tl == VariableTypes.STRING)
        areBoolsOrStrs = tl == VariableTypes.BOOL or tr == VariableTypes.BOOL or tl == VariableTypes.STRING or tr == VariableTypes.STRING
        if operation == '==':
            if areNumAndStrings:
                self._addError(
                    f'Cannot do "{leftValue}" == "{rightValue}". Mismatching types.', lineno)
        elif operation == '!=':
            if areNumAndStrings:
                self._addError(
                    f'Cannot do "{leftValue}" != "{rightValue}". Mismatching types', lineno)
        elif operation == '>=':
            if areBoolsOrStrs:
                self._addError(
                    f'Cannot do "{leftValue}" >= "{rightValue}". Mismatching types', lineno)
        elif operation == '<=':
            if areBoolsOrStrs:
                self._addError(
                    f'Cannot do "{leftValue}" <= "{rightValue}". Mismatching types', lineno)
        elif operation == '>':
            if areBoolsOrStrs:
                self._addError(
                    f'Cannot do "{leftValue}" > "{rightValue}". Mismatching types', lineno)
        elif operation == '<':
            if areBoolsOrStrs:
                self._addError(
                    f'Cannot do "{leftValue}" < "{rightValue}". Mismatching types', lineno)

    def _checkBoolOperator(self, leftType, rightType, leftValue, rightValue, lineno):
        # TODO(hivini): Ask professor about 'and' and 'or' operations between
        # booleans and nums.
        if not (leftType == VariableTypes.BOOL and rightType == VariableTypes.BOOL):
            self._addError(
                f'Cannot perform boolean operation on "{leftValue}" and "{rightValue}"', lineno)

    def _addToNames(self, name: str, type: VariableTypes, value: any):
        if name in self.names:
            self._addError(f'Variable name "{name}" already exists')
        self.names[name] = Variable(type, value)

    def createParser(self):
        parser = yacc.yacc(module=self)
        return parser
