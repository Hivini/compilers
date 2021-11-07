import ply.lex as lex

from enum import Enum


class LexerTypes(Enum):
    INTNUM = 1
    FLOATNUM = 2
    NAME = 3
    INTDCL = 4
    FLOATDCL = 5
    PRINT = 6


class Lexer:
    # List of literals to avoid writing simple regexp for each one.
    literals = ['+', '-', '*', '/', '(', ')', '=']
    # Reserved keywords
    reserved = {
        'int': LexerTypes.INTDCL.name,
        'float': LexerTypes.FLOATDCL.name,
        'print': LexerTypes.PRINT.name
    }
    # Tokens that determine the functions
    tokens = [
        LexerTypes.INTNUM.name,
        LexerTypes.FLOATNUM.name,
        LexerTypes.NAME.name
    ] + list(reserved.values())
    # A string containing ignored characters (spaces and tabs)
    t_ignore = ' \t'

    def __init__(self) -> None:
        self.n_errors = 0
        self.errorToken = ''
        self.errorLine = -1

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
