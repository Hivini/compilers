import ply.yacc as yacc

from compiler.lexer import Lexer
from enum import Enum
from typing import List


class ParserError(Exception):
    pass


class SymbolTable:
    def __init__(self, table, parent):
        self.table = table
        self.parent = parent
        self.children = []

    def __str__(self) -> str:
        return str(self.table)

    def __repr__(self) -> str:
        return str(self.table)


class VariableTypes(Enum):
    INT = 1
    FLOAT = 2
    STRING = 3
    BOOL = 4


class Variable:
    def __init__(self, type: VariableTypes, lineno: any, value: any = None) -> None:
        self.type = type
        self.lineno = lineno
        self.value = None

    def __str__(self) -> str:
        if self.value:
            return f'| Type: {self.type}, Line: {self.lineno}, Value: {self.value} |'
        return f'| Type: {self.type}, Line: {self.lineno} |'

    def __repr__(self) -> str:
        if self.value:
            return f'| Type: {self.type}, Line: {self.lineno}, Value: {self.value} |'
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
    WHILE_STATEMENT = 26
    FOR_STATEMENT = 27
    REASSIGN = 28
    INT_TO_FLOAT = 29
    SUM = 50
    SUBSTRACT = 51
    MULTIPLICATION = 52
    DIVISION = 53
    UMINUS = 54
    EXPONENT = 55


class ASTNode:
    def __init__(self, type: ASTTypes, children: List[any] = None,
                 variableType: VariableTypes = None, variableValue: any = None,
                 variableName: str = None, symbolTable: SymbolTable = None, lineno: int = None):
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

    def __init__(self, proglines) -> None:
        self.lexerInstance = Lexer()
        self.lexer = self.lexerInstance.createLexer()
        self.tokens = self.lexerInstance.tokens
        self.start = 'program'
        self.first_error = ''
        self.proglines = proglines
        self.symbolTable = None
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
                        | block_statement
        '''
        p[0] = p[1]

    def p_block_statement(self, p):
        '''block_statement : if_statement
                            | while_statement
                            | for_statement
        '''
        p[0] = p[1]

    def p_for_statement(self, p):
        '''for_statement : FOR "(" statement SENTENCE_END declaration SENTENCE_END statement ")" "{" program "}" '''
        if p[3].type != ASTTypes.INT_DCL:
            self._addError(
                'Invalid for loop variable initialization', p.lineno(2))
        self._checkIsValidBoolCondition(p[5].type, p.lineno(2))
        if p[7].type != ASTTypes.REASSIGN:
            self._addError('Invalid for loop updation', p.lineno(2))
        p[0] = ASTNode(ASTTypes.FOR_STATEMENT, children=[
                       p[3], p[5], p[7], p[10]], lineno=p.lineno(1))

    def p_while_statement(self, p):
        '''while_statement : WHILE "(" declaration ")" "{" program "}" '''
        self._checkIsValidBoolCondition(p[3].type, p.lineno(2))
        p[0] = ASTNode(ASTTypes.WHILE_STATEMENT, children=[
                       p[3], p[6]], lineno=p.lineno(1))

    def p_if_statement(self, p):
        '''if_statement : IF "(" declaration ")" "{" program "}" elif else '''
        self._checkIsValidBoolCondition(p[3].type, p.lineno(2))
        ifNode = ASTNode(ASTTypes.IF, children=[
                         p[3], p[6]], lineno=p.lineno(1))
        children = [ifNode]
        # Elifs
        if (p[8] != None):
            children.extend(p[8])
        # Else
        if (p[9] != None):
            children.append(p[9])
        p[0] = ASTNode(ASTTypes.IF_STATEMENT, children=children)

    def p_block_elif(self, p):
        '''elif : ELIF "(" declaration ")" "{" program "}" elif
                |
        '''
        if len(p) > 1:
            self._checkIsValidBoolCondition(p[3].type, p.lineno(2))
            children = [p[3]]
            if (p[6] != None):
                children.append(p[6])
            currentElifs = [ASTNode(
                ASTTypes.ELIF, children=children, lineno=p.lineno(1))]
            if (p[8] != None):
                currentElifs.extend(p[8])
            p[0] = currentElifs

    def p_block_else(self, p):
        '''else : ELSE "{" program "}"
                |
        '''
        if len(p) > 1:
            children = []
            if (p[3] != None):
                children.append(p[3])
            p[0] = ASTNode(ASTTypes.ELSE, children=children,
                           lineno=p.lineno(1))

    def p_statement_declare_int(self, p):
        '''statement : INTDCL NAME assignment
                        | INTDCL NAME
        '''
        tmpNode = ASTNode(
            ASTTypes.INT_DCL, variableName=p[2], variableType=VariableTypes.INT, lineno=p.lineno(2))
        if len(p) == 4:
            tmpNode.children = [p[3]]
        p[0] = tmpNode

    def p_statement_declare_float(self, p):
        '''statement : FLOATDCL NAME assignment
                        | FLOATDCL NAME
        '''
        tmpNode = ASTNode(
            ASTTypes.FLOAT_DCL, variableName=p[2], variableType=VariableTypes.FLOAT, lineno=p.lineno(2))
        if len(p) == 4:
            tmpNode.children = [p[3]]
        p[0] = tmpNode

    def p_statement_declare_string(self, p):
        '''statement : STRING_DCL NAME assignment
                        | STRING_DCL NAME
        '''
        tmpNode = ASTNode(
            ASTTypes.STRING_DCL, variableName=p[2], variableType=VariableTypes.STRING, lineno=p.lineno(2))
        if len(p) == 4:
            tmpNode.children = [p[3]]
        p[0] = tmpNode

    def p_statement_declare_boolean(self, p):
        '''statement : BOOL_DCL NAME assignment
                        | BOOL_DCL NAME
        '''
        tmpNode = ASTNode(
            ASTTypes.BOOL_DCL, variableName=p[2], variableType=VariableTypes.BOOL, lineno=p.lineno(2))
        if len(p) == 4:
            tmpNode.children = [p[3]]
        p[0] = tmpNode

    def p_statement_assign_variable(self, p):
        '''statement : NAME assignment '''
        p[0] = ASTNode(ASTTypes.REASSIGN, children=[p[2]],
                       lineno=p.lineno(1), variableName=p[1])

    def p_assignment(self, p):
        '''assignment : '=' declaration '''
        p[0] = ASTNode(ASTTypes.ASSIGN, children=[p[2]], lineno=p.lineno(1))

    def p_expression_print(self, p):
        '''statement : PRINT '(' declaration ')' '''
        p[0] = ASTNode(ASTTypes.PRINT, [p[3]], lineno=p.lineno(1))

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

    def _produceSymbolTable(self, root: ASTNode, currentTable: SymbolTable, pending: List[ASTNode] = None):
        if root.type == ASTTypes.FOR_STATEMENT:
            # Save for future processing.
            self._produceSymbolTable(
                root.children[3], currentTable, root.children[:3])
            return
        if root.type == ASTTypes.BLOCK:
            # Global variables
            if currentTable == None:
                root.symbolTable = SymbolTable({}, None)
            else:
                root.symbolTable = SymbolTable({}, currentTable)
                root.symbolTable.parent.children.append(root.symbolTable)
            currentTable = root.symbolTable
            if pending != None:
                for node in pending:
                    self._produceSymbolTable(node, currentTable, None)
                pending = None
        elif root.type in [ASTTypes.INT_DCL, ASTTypes.FLOAT_DCL, ASTTypes.STRING_DCL, ASTTypes.BOOL_DCL]:
            for c in root.children:
                self._produceSymbolTable(c, currentTable, pending)
            self._addToNames(currentTable, root.variableName,
                             root.variableType, root.lineno)
            return
        elif root.type in [ASTTypes.VARIABLE, ASTTypes.REASSIGN]:
            self._checkIfVariableExist(
                currentTable, root.variableName, root.lineno)
        for c in root.children:
            self._produceSymbolTable(c, currentTable, pending)

    def _addToNames(self, symbolTable: SymbolTable, name: str, type: VariableTypes, lineno: int):
        currentSymbolTable = symbolTable
        while currentSymbolTable != None:
            if name in currentSymbolTable.table:
                self._addError(
                    f'Variable name "{name}" already exists', lineno)
            currentSymbolTable = currentSymbolTable.parent
        symbolTable.table[name] = Variable(type, lineno)

    def _checkIfVariableExist(self, symbolTable: SymbolTable, name: str, lineno: int):
        currentSymbolTable = symbolTable
        while currentSymbolTable != None:
            if name in currentSymbolTable.table:
                return
            currentSymbolTable = currentSymbolTable.parent
        self._addError(f'Variable name "{name}" does not exist', lineno)

    def _checkIsValidBoolCondition(self, nodeType: ASTTypes, lineno: int):
        compareTypes = [ASTTypes.CMP_EQUAL, ASTTypes.CMP_NOT_EQUAL, ASTTypes.CMP_GREATER_EQUAL,
                        ASTTypes.CMP_LESS_EQUAL, ASTTypes.CMP_GREATER, ASTTypes.CMP_LESS]
        boolOpTypes = [ASTTypes.AND_OP, ASTTypes.OR_OP]
        validOptions = [ASTTypes.BOOL_FALSE,
                        ASTTypes.BOOL_TRUE, ASTTypes.VARIABLE]
        validOptions.extend(compareTypes)
        validOptions.extend(boolOpTypes)
        if nodeType not in validOptions:
            self._addError('Invalid bool condition encountered', lineno)

    def parseProgram(self, prog):
        root = self.parser.parse(prog)
        self._produceSymbolTable(root, None)
        self.symbolTable = root.symbolTable
        return root
