import ply.yacc as yacc

from compiler.lexer import Lexer
from enum import Enum
from typing import List


class ParserError(Exception):
    pass


class ASTTypes(Enum):
    PROGRAM = 0
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
    BLOCK = 26
    SUM = 50
    SUBSTRACT = 51
    MULTIPLICATION = 52
    DIVISION = 53
    UMINUS = 54
    EXPONENT = 55


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


class TreeNode:
    def __init__(self, type: ASTTypes, children: List[any] = None, value: any = None):
        self.type = type
        if children:
            self.children = children
        else:
            self.children = []
        self.value = value

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

    def __init__(self) -> None:
        self.lexerInstance = Lexer()
        self.lexer = self.lexerInstance.createLexer()
        self.tokens = self.lexerInstance.tokens
        self.start = 'program'
        self.first_error = ''

    def _addError(self, error):
        self.first_error = error
        raise ParserError('Parser Error!')

    def p_program(self, p):
        '''program : expression program
                    | expression
        '''
        if len(p) == 3:
            children = [p[1]]
            children.extend(p[2].children)
            p[0] = TreeNode(ASTTypes.PROGRAM, children)
        else:
            p[0] = TreeNode(ASTTypes.PROGRAM, [p[1]])

    def p_line(self, p):
        '''expression : statement SENTENCE_END
                        | block
        '''
        p[0] = p[1]


    def p_block_if(self, p):
        '''block : IF "(" declaration ")" "{" program "}" elif else '''
        if not isinstance(p[3].value, bool):
            self._addError(
                'If expression must have a boolean value in the declaration.')
        ifchildren = [p[3]]
        if (p[6] != None):
            ifchildren.append(p[6])
        ifNode = TreeNode(ASTTypes.IF, children=ifchildren, value=p[3].value)
        children = [ifNode]
        if (p[8] != None):
            children.append(p[8])
        if (p[9] != None):
            children.append(p[9])
        p[0] = TreeNode(ASTTypes.IF_STATEMENT, children=children, value=None)

    def p_block_elif(self, p):
        '''elif : ELIF "(" declaration ")" "{" program "}" elif
                |
        '''
        if len(p) > 1:
            if not isinstance(p[3].value, bool):
                self._addError(
                    'Elif expression must have a boolean value in the declaration.')
            children = [p[3]]
            if (p[6] != None):
                children.append(p[6])
            if (p[8] != None):
                children.append(p[8])
            if len(p) > 1:
                p[0] = TreeNode(
                    ASTTypes.ELIF, children=children, value=p[3].value)

    def p_block_else(self, p):
        '''else : ELSE "{" program "}"
                |
        '''
        if len(p) > 1:
            children = []
            if (p[3] != None):
                children.append(p[3])
            if len(p) > 1:
                p[0] = TreeNode(
                    ASTTypes.ELSE, children=children, value=p[3].value)

    def p_statement_declare_int(self, p):
        '''statement : INTDCL NAME assignment
        '''
        if not isinstance(p[3].value, int):
            self._addError(f'"{p[3].value}" value cannot be assigned to int.')
        tmp = TreeNode(ASTTypes.INT_DCL, children=[p[3]], value=p[2])
        self._addToNames(p[2], VariableTypes.INT, p[3].value)
        p[0] = tmp

    def p_statement_declare_float(self, p):
        '''statement : FLOATDCL NAME assignment
        '''
        if isinstance(p[3].value, int):
            p[3].value = float(p[3].value)
        elif not isinstance(p[3].value, float):
            self._addError(
                f'"{p[3].value}" value cannot be assigned to float.')
        tmp = TreeNode(ASTTypes.FLOAT_DCL, children=[p[3]], value=p[2])
        self._addToNames(p[2], VariableTypes.FLOAT, p[3].value)
        p[0] = tmp

    def p_statement_declare_string(self, p):
        '''statement : STRING_DCL NAME assignment
        '''
        if not isinstance(p[3].value, str):
            self._addError(
                f'"{p[3].value}" value cannot be assigned to string.')
        tmp = TreeNode(ASTTypes.STRING_DCL, children=[p[3]], value=p[2])
        self._addToNames(p[2], VariableTypes.STRING, p[3].value)
        p[0] = tmp

    def p_statement_declare_boolean(self, p):
        '''statement : BOOL_DCL NAME assignment
        '''
        if not isinstance(p[3].value, bool):
            self._addError(
                f'"{p[3].value}" value cannot be assigned to boolean.')
        tmp = TreeNode(ASTTypes.BOOL_DCL, children=[p[3]], value=p[2])
        self._addToNames(p[2], VariableTypes.BOOL, p[3].value)
        p[0] = tmp

    def p_assignment(self, p):
        '''assignment : '=' declaration '''
        p[0] = TreeNode(ASTTypes.ASSIGN, children=[p[2]], value=p[2].value)

    def p_expression_print(self, p):
        '''statement : PRINT '(' declaration ')' '''
        p[0] = TreeNode(ASTTypes.PRINT, [p[3]])

    def p_expression_binop(self, p):
        '''declaration : declaration '+' declaration
                    | declaration '-' declaration
                    | declaration '*' declaration
                    | declaration '/' declaration
                    | declaration '^' declaration
        '''
        leftV = p[1].value
        rightV = p[3].value
        op = p[2]
        self._checkArithmeticOperation(leftV, rightV, op)
        if p[2] == '+':
            if type(leftV) == str or type(rightV) == str:
                p[0] = TreeNode(ASTTypes.SUM, value=str(
                    leftV) + str(rightV), children=[p[1], p[3]])
            else:
                p[0] = TreeNode(ASTTypes.SUM, value=leftV +
                                rightV, children=[p[1], p[3]])
        elif p[2] == '-':
            p[0] = TreeNode(ASTTypes.SUBSTRACT, value=leftV -
                            rightV, children=[p[1], p[3]])
        elif p[2] == '*':
            p[0] = TreeNode(ASTTypes.MULTIPLICATION,
                            value=leftV * rightV, children=[p[1], p[3]])
        elif p[2] == '/':
            val = leftV / rightV
            if val.is_integer():
                val = int(val)
            p[0] = TreeNode(ASTTypes.DIVISION, value=val,
                            children=[p[1], p[3]])
        elif p[2] == '^':
            p[0] = TreeNode(ASTTypes.EXPONENT, value=pow(
                leftV, rightV), children=[p[1], p[3]])

    def p_expression_cmpop(self, p):
        '''declaration : declaration EQUALS declaration
                    | declaration NOT_EQUAL declaration
                    | declaration GREATER_EQUAL declaration
                    | declaration LESS_EQUAL declaration
                    | declaration '>' declaration
                    | declaration '<' declaration
        '''
        leftV = p[1].value
        rightV = p[3].value
        op = p[2]
        self._checkComparisonOperation(leftV, rightV, op)
        if op == '==':
            p[0] = TreeNode(ASTTypes.CMP_EQUAL, value=leftV ==
                            rightV, children=[p[1], p[3]])
        elif op == '!=':
            p[0] = TreeNode(ASTTypes.CMP_NOT_EQUAL, value=leftV !=
                            rightV, children=[p[1], p[3]])
        elif op == '>=':
            p[0] = TreeNode(ASTTypes.CMP_GREATER_EQUAL, value=leftV >=
                            rightV, children=[p[1], p[3]])
        elif p[2] == '<=':
            p[0] = TreeNode(ASTTypes.CMP_LESS_EQUAL, value=leftV <=
                            rightV, children=[p[1], p[3]])
        elif p[2] == '>':
            p[0] = TreeNode(ASTTypes.CMP_GREATER, value=leftV >
                            rightV, children=[p[1], p[3]])
        elif p[2] == '<':
            p[0] = TreeNode(ASTTypes.CMP_LESS, value=leftV <
                            rightV, children=[p[1], p[3]])

    def p_expression_boolop(self, p):
        '''declaration : declaration AND_OP declaration
                    | declaration OR_OP declaration
        '''
        self._checkBoolOperator(p[1].value, p[3].value, p[2])
        if p[2] == 'and':
            p[0] = TreeNode(ASTTypes.AND_OP, value=p[1].value and
                            p[3].value, children=[p[1], p[3]])
        elif p[2] == 'or':
            p[0] = TreeNode(ASTTypes.OR_OP, value=p[1].value or
                            p[3].value, children=[p[1], p[3]])

    def p_expression_group(self, p):
        '''declaration : '(' declaration ')' '''
        p[0] = p[2]

    def p_expression_uminus(self, t):
        '''declaration : - declaration %prec UMINUS'''
        t[0] = TreeNode(ASTTypes.UMINUS, value=-t[2].value, children=[t[2]])

    def p_expression_intnum(self, p):
        '''declaration : INTNUM '''
        p[0] = TreeNode(ASTTypes.INT, value=p[1])

    def p_expression_floatnum(self, p):
        '''declaration : FLOATNUM '''
        p[0] = TreeNode(ASTTypes.FLOAT, value=p[1])

    def p_expression_bool_true(self, p):
        '''declaration : BOOL_TRUE '''
        p[0] = TreeNode(ASTTypes.BOOL_TRUE, value=True)

    def p_expression_bool_false(self, p):
        '''declaration : BOOL_FALSE '''
        p[0] = TreeNode(ASTTypes.BOOL_FALSE, value=False)

    def p_expression_string(self, p):
        '''declaration : STRING '''
        p[0] = TreeNode(ASTTypes.STRING, value=p[1].replace('"', ''))

    def p_expression_name(self, p):
        '''declaration : NAME '''
        if (p[1] in self.names):
            p[0] = TreeNode(ASTTypes.VARIABLE, value=self.names[p[1]].value)
        else:
            self._addError(f'Variable {p[1]} does not exist.')

    def p_error(self, p):
        self._addError('Syntax error!')

    def _checkArithmeticOperation(self, leftValue, rightValue, operation: str):
        numTypes = [int, float]
        bothAreNums = type(leftValue) in numTypes and type(
            rightValue) in numTypes
        if operation == '+':
            if type(leftValue) == bool or type(rightValue) == bool:
                self._addError(
                    f'Cannot sum values "{leftValue}" and "{rightValue}"')
        elif operation == '-':
            if not(bothAreNums):
                self._addError(
                    f'Cannot substract values "{leftValue}" and "{rightValue}".')
        elif operation == '*':
            if not(bothAreNums):
                self._addError(
                    f'Cannot multiply values "{leftValue}" and "{rightValue}".')
        elif operation == '/':
            if not(bothAreNums):
                self._addError(
                    f'Cannot divide values "{leftValue}" and "{rightValue}".')
            elif rightValue == 0:
                self._addError(
                    f'{leftValue} / {rightValue} is invalid. Cannot perform division by zero.')
        elif operation == '^':
            if not(bothAreNums):
                self._addError(
                    f'Cannot get the exponent of "{leftValue}" ^ "{rightValue}".')

    def _checkComparisonOperation(self, leftValue, rightValue, operation: str):
        numTypes = [int, float]
        tl = type(leftValue)
        tr = type(rightValue)
        areNumAndStrings = (tl in numTypes and tr == str) or (
            tr in numTypes and tl == str)
        areBoolsOrStrs = tl == bool or tr == bool or tl == str or tr == str
        if operation == '==':
            if areNumAndStrings:
                self._addError(
                    f'Cannot do "{leftValue}" == "{rightValue}". Mismatching types.')
        elif operation == '!=':
            if areNumAndStrings:
                self._addError(
                    f'Cannot do "{leftValue}" != "{rightValue}". Mismatching types.')
        elif operation == '>=':
            if areBoolsOrStrs:
                self._addError(
                    f'Cannot do "{leftValue}" >= "{rightValue}". Mismatching types.')
        elif operation == '<=':
            if areBoolsOrStrs:
                self._addError(
                    f'Cannot do "{leftValue}" <= "{rightValue}". Mismatching types.')
        elif operation == '>':
            if areBoolsOrStrs:
                self._addError(
                    f'Cannot do "{leftValue}" > "{rightValue}". Mismatching types.')
        elif operation == '<':
            if areBoolsOrStrs:
                self._addError(
                    f'Cannot do "{leftValue}" < "{rightValue}". Mismatching types.')

    def _checkBoolOperator(self, leftValue, rightValue, operation: str):
        tl = type(leftValue)
        tr = type(rightValue)
        # TODO(hivini): Ask professor about 'and' and 'or' operations between
        # booleans and nums.
        if not (tl == bool and tr == bool):
            self._addError(
                f'Cannot perform boolean operation on "{leftValue}" and "{rightValue}".')

    def _addToNames(self, name: str, type: VariableTypes, value: any):
        if name in self.names:
            self._addError(f'Variable name "{name}" already exists.')
        self.names[name] = Variable(type, value)

    def createParser(self):
        parser = yacc.yacc(module=self)
        return parser
