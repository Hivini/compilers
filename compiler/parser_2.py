import ply.yacc as yacc

from compiler.lexer import Lexer
from enum import Enum
from typing import Dict, List


class ParserError(Exception):
    pass


class VariableTypes(Enum):
    INT = 1
    FLOAT = 2
    STRING = 3
    BOOL = 4


class Variable:
    def __init__(self, type: VariableTypes, lineno: any) -> None:
        self.type = type
        self.lineno = lineno

    def __str__(self) -> str:
        return f'| Type: {self.type}, Line: {self.lineno} |'

    def __repr__(self) -> str:
        return f'| Type: {self.type}, Line: {self.lineno} |'


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
                 variableName: str = None, symbolTable=None, lineno: int = None):
        self.type = type
        if children:
            self.children = children
        else:
            self.children = []
        self.variableType = variableType
        self.variableValue = variableValue
        self.variableName = variableName
        self.symbolTable = symbolTable
        self.lineno = lineno

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
        self.parser = yacc.yacc(module=self)

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
        p[0] = ASTNode(ASTTypes.INT_DCL, children=[p[3]],
                       variableName=p[2], variableType=VariableTypes.INT, lineno=p.lineno(2))

    def p_statement_declare_float(self, p):
        '''statement : FLOATDCL NAME assignment
        '''
        p[0] = ASTNode(ASTTypes.FLOAT_DCL, children=[p[3]],
                       variableName=p[2], variableType=VariableTypes.FLOAT, lineno=p.lineno(2))

    def p_statement_declare_string(self, p):
        '''statement : STRING_DCL NAME assignment
        '''
        p[0] = ASTNode(ASTTypes.STRING_DCL, children=[p[3]],
                       variableName=p[2], variableType=VariableTypes.STRING, lineno=p.lineno(2))

    def p_statement_declare_boolean(self, p):
        '''statement : BOOL_DCL NAME assignment
        '''
        p[0] = ASTNode(ASTTypes.BOOL_DCL, children=[p[3]],
                       variableName=p[2], variableType=VariableTypes.BOOL, lineno=p.lineno(2))

    def p_assignment(self, p):
        '''assignment : '=' declaration '''
        p[0] = ASTNode(ASTTypes.ASSIGN, children=[p[2]], lineno=p.lineno(1))

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
        if p[2] == '+':
            p[0] = ASTNode(ASTTypes.SUM, children=[
                           p[1], p[3]], lineno=p.lineno(2))
        elif p[2] == '-':
            p[0] = ASTNode(
                ASTTypes.SUBSTRACT, children=[p[1], p[3]], lineno=p.lineno(2))
        elif p[2] == '*':
            p[0] = ASTNode(
                ASTTypes.MULTIPLICATION, children=[p[1], p[3]], lineno=p.lineno(2))
        elif p[2] == '/':
            p[0] = ASTNode(ASTTypes.DIVISION, children=[
                           p[1], p[3]], lineno=p.lineno(2))
        elif p[2] == '^':
            p[0] = ASTNode(ASTTypes.EXPONENT, children=[
                           p[1], p[3]], lineno=p.lineno(2))

    def p_expression_cmpop(self, p):
        '''declaration : declaration EQUALS declaration
                    | declaration NOT_EQUAL declaration
                    | declaration GREATER_EQUAL declaration
                    | declaration LESS_EQUAL declaration
                    | declaration '>' declaration
                    | declaration '<' declaration
        '''
        if p[2] == '==':
            p[0] = ASTNode(ASTTypes.CMP_EQUAL, children=[
                           p[1], p[3]], lineno=p.lineno(2))
        elif p[2] == '!=':
            p[0] = ASTNode(ASTTypes.CMP_NOT_EQUAL, children=[
                           p[1], p[3]], lineno=p.lineno(2))
        elif p[2] == '>=':
            p[0] = ASTNode(ASTTypes.CMP_GREATER_EQUAL, children=[
                           p[1], p[3]], lineno=p.lineno(2))
        elif p[2] == '<=':
            p[0] = ASTNode(ASTTypes.CMP_LESS_EQUAL, children=[
                           p[1], p[3]], lineno=p.lineno(2))
        elif p[2] == '>':
            p[0] = ASTNode(ASTTypes.CMP_GREATER, children=[
                           p[1], p[3]], lineno=p.lineno(2))
        elif p[2] == '<':
            p[0] = ASTNode(ASTTypes.CMP_LESS, children=[
                           p[1], p[3]], lineno=p.lineno(2))

    def p_expression_boolop(self, p):
        '''declaration : declaration AND_OP declaration
                    | declaration OR_OP declaration
        '''
        if p[2] == 'and':
            p[0] = ASTNode(ASTTypes.AND_OP, children=[
                           p[1], p[3]], lineno=p.lineno(2))
        elif p[2] == 'or':
            p[0] = ASTNode(ASTTypes.OR_OP, children=[
                           p[1], p[3]], lineno=p.lineno(2))

    def p_expression_group(self, p):
        '''declaration : '(' declaration ')' '''
        p[0] = p[2]

    def p_expression_uminus(self, p):
        '''declaration : - declaration %prec UMINUS'''
        p[0] = ASTNode(ASTTypes.UMINUS, children=[p[2]], lineno=p.lineno(1))

    def p_expression_intnum(self, p):
        '''declaration : INTNUM '''
        p[0] = ASTNode(
            ASTTypes.INT, variableType=VariableTypes.INT, variableValue=int(p[1]), lineno=p.lineno(1))

    def p_expression_floatnum(self, p):
        '''declaration : FLOATNUM '''
        p[0] = ASTNode(
            ASTTypes.FLOAT, variableType=VariableTypes.FLOAT, variableValue=float(p[1]), lineno=p.lineno(1))

    def p_expression_bool_true(self, p):
        '''declaration : BOOL_TRUE '''
        p[0] = ASTNode(ASTTypes.BOOL_TRUE,
                       variableType=VariableTypes.BOOL, variableValue=True, lineno=p.lineno(1))

    def p_expression_bool_false(self, p):
        '''declaration : BOOL_FALSE '''
        p[0] = ASTNode(ASTTypes.BOOL_FALSE,
                       variableType=VariableTypes.BOOL, variableValue=False, lineno=p.lineno(1))

    def p_expression_string(self, p):
        '''declaration : STRING '''
        p[0] = ASTNode(ASTTypes.STRING,
                       variableType=VariableTypes.STRING, variableValue=p[1].replace('"', ''), lineno=p.lineno(1))

    def p_expression_name(self, p):
        '''declaration : NAME '''
        p[0] = ASTNode(ASTTypes.VARIABLE, variableName=p[1],
                       lineno=p.lineno(1))

    def p_error(self, p):
        if p:
            self._addError(
                f'Unexpected symbol "{p.value}", at line {p.lineno}', p.lineno)
        self._addError('Unexpected end of file reached')

    # def _produceSymbolHelper(current):
    def _produceSymbolTable(self, root):
        if root.type in [ASTTypes.INT_DCL, ASTTypes.FLOAT_DCL, ASTTypes.STRING_DCL, ASTTypes.BOOL_DCL]:
            self._addToNames(root.variableName, root.variableType, root.lineno)
        for c in root.children:
            self._produceSymbolTable(c)

    def _addToNames(self, name: str, type: VariableTypes, lineno: int):
        if name in self.names:
            self._addError(f'Variable name "{name}" already exists', lineno)
        self.names[name] = Variable(type, lineno)

    def parseProgram(self, prog):
        root = self.parser.parse(prog)
        self._produceSymbolTable(root)
        return root
