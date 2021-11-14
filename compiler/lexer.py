import ply.lex as lex

from enum import Enum


class LexerTypes(Enum):
    INTNUM = 1
    FLOATNUM = 2
    NAME = 3
    INTDCL = 4
    FLOATDCL = 5
    PRINT = 6
    AND_OP = 7
    OR_OP = 8
    BOOL_TRUE = 9
    BOOL_FALSE = 10
    BOOL_DCL = 11
    EQUALS = 12
    NOT_EQUAL = 13
    GREATER_EQUAL = 14
    LESS_EQUAL = 15
    WHILE = 16
    FOR = 17
    IF = 18
    ELIF = 19
    ELSE = 20
    STRING_DCL = 21
    STRING = 22
    SENTENCE_END = 23


class Lexer:
    # List of literals to avoid writing simple regexp for each one.
    literals = ['+', '-', '*', '/', '=', '^',
                '>', '<', '(', ')', '{', '}', '"']
    # Reserved keywords
    reserved = {
        'int': LexerTypes.INTDCL.name,
        'float': LexerTypes.FLOATDCL.name,
        'print': LexerTypes.PRINT.name,
        'and': LexerTypes.AND_OP.name,
        'or': LexerTypes.OR_OP.name,
        'if': LexerTypes.IF.name,
        'elif': LexerTypes.ELIF.name,
        'else': LexerTypes.ELSE.name,
        'while': LexerTypes.WHILE.name,
        'for': LexerTypes.FOR.name,
        'string': LexerTypes.STRING_DCL.name,
        'bool': LexerTypes.BOOL_DCL.name,
        'true': LexerTypes.BOOL_TRUE.name,
        'false': LexerTypes.BOOL_FALSE.name,
    }
    # Tokens that determine the functions
    tokens = [
        LexerTypes.INTNUM.name,
        LexerTypes.FLOATNUM.name,
        LexerTypes.NAME.name,
        LexerTypes.EQUALS.name,
        LexerTypes.NOT_EQUAL.name,
        LexerTypes.GREATER_EQUAL.name,
        LexerTypes.LESS_EQUAL.name,
        LexerTypes.SENTENCE_END.name,
        LexerTypes.STRING.name,
    ] + list(reserved.values())

    t_EQUALS = r'=='
    t_NOT_EQUAL = r'!='
    t_GREATER_EQUAL = r'>='
    t_LESS_EQUAL = r'<='
    t_SENTENCE_END = r';'
    # A string containing ignored characters (spaces and tabs)
    t_ignore = ' \t'

    def __init__(self) -> None:
        self.n_errors = 0
        self.errorToken = ''
        self.errorLine = -1

    def t_STRING(self, t):
        r'"([^"\n]|(\\"))*"'
        t.type = LexerTypes.STRING.name
        return t

    def t_NAME(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value, LexerTypes.NAME.name)
        return t

    def t_FNUMBER(self, t):
        r'\d+\.\d+'
        t.value = float(t.value)
        t.type = LexerTypes.FLOATNUM.name
        return t

    def t_INUMBER(self, t):
        r'\d+'
        t.value = int(t.value)
        t.type = LexerTypes.INTNUM.name
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        self.n_errors += 1
        self.errorLine = t.lexer.lineno - 1
        self.errorToken = t.value[0]
        t.lexer.skip(1)

    def createLexer(self):
        lexer = lex.lex(module=self)
        return lexer
