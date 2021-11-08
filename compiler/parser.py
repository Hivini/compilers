import ply.yacc as yacc

from compiler.lexer import Lexer


class Parser:
    names = {}
    abstractTree = []

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

    def p_line(self, p):
        '''expression : statement SENTENCE_END '''

    def p_expression_print(self, p):
        '''statement : PRINT '(' expression ')' '''
        print(p[3])

    def p_expression(self, p):
        '''expression : NAME '''
        p[0] = p[1]

    def p_error(self, p):
        self.total_errors += 1

    def createParser(self):
        parser = yacc.yacc(module=self)
        return parser
