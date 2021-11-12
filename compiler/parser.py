import ply.yacc as yacc

from compiler.lexer import Lexer
from enum import Enum
from typing import List


class ASTTypes(Enum):
    PROGRAM = 0
    PRINT = 1
    VARIABLE = 2
    ASSIGN = 3
    INT = 4
    INT_DCL = 5
    FLOAT = 6
    FLOAT_DCL = 7
    SUM = 50
    SUBSTRACT = 51
    MULTIPLICATION = 52
    DIVISION = 53
    UMINUS = 54

class VariableTypes(Enum):
    INT = 1
    FLOAT = 2

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
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right','UMINUS'),
    )
    names = {}

    def __init__(self) -> None:
        self.lexerInstance = Lexer()
        self.lexer = self.lexerInstance.createLexer()
        self.tokens = self.lexerInstance.tokens
        self.start = 'program'
        self.total_errors = 0
        self.first_error = ''

    def _addError(self, error):
        if (self.total_errors == 0):
            self.first_error = error
        self.total_errors += 1

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
        '''expression : statement SENTENCE_END '''
        p[0] = p[1]

    def p_statement_declare_int(self, p):
        '''statement : INTDCL NAME assignment
        '''
        if type(p[3].value) == float:
            if p[3].value.is_integer():
                p[3].value = int(p[3].value)
            else:
                self._addError('Float value cannot be assigned to int.')
                return
        tmp = TreeNode(ASTTypes.INT_DCL, children=[p[3]], value=p[2])
        self.names[p[2]] = Variable(VariableTypes.INT, p[3].value)
        p[0] = tmp

    def p_statement_declare_float(self, p):
        '''statement : FLOATDCL NAME assignment
        '''
        tmp = TreeNode(ASTTypes.FLOAT_DCL, children=[p[3]], value=p[2])
        self.names[p[2]] = Variable(VariableTypes.FLOAT, p[3].value)
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
        '''
        if p[2] == '+':
            p[0] = TreeNode(ASTTypes.SUM, value=p[1].value + p[3].value, children=[p[1], p[3]])
        elif p[2] == '-':
            p[0] = TreeNode(ASTTypes.SUBSTRACT, value=p[1].value - p[3].value, children=[p[1], p[3]])
        elif p[2] == '*':
            p[0] = TreeNode(ASTTypes.MULTIPLICATION, value=p[1].value * p[3].value, children=[p[1], p[3]])
        elif p[2] == '/':
            if p[3].value == 0:
                print('Division times 0 :(')
            else:
                p[0] = TreeNode(ASTTypes.DIVISION, value=p[1].value / p[3].value, children=[p[1], p[3]])

    def p_expression_group(self, p):
        '''declaration : '(' declaration ')' '''
        p[0] = p[2]

    def p_expression_uminus(self, t):
        '''declaration : - declaration %prec UMINUS'''
        t[0] = TreeNode(ASTTypes.UMINUS, value=-t[2].value, children=[t[2]])

    def p_expression_intnum(self, p):
        '''declaration : INTNUM '''
        p[0] = TreeNode(ASTTypes.INT, value=p[1])

    def p_expression_floatnumn(self, p):
        '''declaration : FLOATNUM '''
        p[0] = TreeNode(ASTTypes.FLOAT, value=p[1])

    def p_expression_name(self, p):
        '''declaration : NAME '''
        if (p[1] in self.names):
            p[0] = TreeNode(ASTTypes.VARIABLE, value=self.names[p[1]].value)
        else:
            self._addError(f'Variable {p[1]} does not exist.')
            
    def p_error(self, p):
        self._addError('Syntax error!')

    def createParser(self):
        parser = yacc.yacc(module=self)
        return parser
