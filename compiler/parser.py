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
    SUM = 50
    SUBSTRACT = 51
    MULTIPLICATION = 52
    DIVISION = 53


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
    )
    names = {}

    def __init__(self) -> None:
        self.lexerInstance = Lexer()
        self.lexer = self.lexerInstance.createLexer()
        self.tokens = self.lexerInstance.tokens
        self.start = 'program'
        self.total_errors = 0

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
        # TODO(hivini): Check for floats.
        tmp = TreeNode(ASTTypes.INT_DCL, children=[p[3]], value=p[2])
        self.names[p[2]] = { "type": "INT", "value": p[3].value}
        p[0] = tmp
        print(self.names)

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

    def p_expression_intnum(self, p):
        '''declaration : INTNUM '''
        p[0] = TreeNode(ASTTypes.INT, value=p[1])

    def p_expression_name(self, p):
        '''declaration : NAME '''
        # TODO(hivini): Check if name exists.
        p[0] = TreeNode(ASTTypes.VARIABLE, value=p[1])

    def p_error(self, p):
        self.total_errors += 1

    def createParser(self):
        parser = yacc.yacc(module=self)
        return parser
