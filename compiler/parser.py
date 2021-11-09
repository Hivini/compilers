import ply.yacc as yacc

from compiler.lexer import Lexer
from enum import Enum
from typing import List


class ASTTypes(Enum):
    PROGRAM = 0
    PRINT = 1
    VARIABLE = 2


class TreeNode:
    def __init__(self, type: ASTTypes, children: List[any] = None, value: any = None):
        self.type = type
        if children:
            self.children = children
        else:
            self.children = []
        self.value = value


class Parser:
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
            p[0] = TreeNode(ASTTypes.PROGRAM, [p[1], p[2]])
        else:
            p[0] = TreeNode(ASTTypes.PROGRAM, [p[1]])

    def p_line(self, p):
        '''expression : statement SENTENCE_END '''
        p[0] = p[1]

    def p_expression_print(self, p):
        '''statement : PRINT '(' expression ')' '''
        p[0] = TreeNode(ASTTypes.PRINT, [p[3]])

    def p_expression(self, p):
        '''expression : NAME '''
        p[0] = TreeNode(ASTTypes.VARIABLE, value=p[1])

    def p_error(self, p):
        self.total_errors += 1

    def createParser(self):
        parser = yacc.yacc(module=self)
        return parser
