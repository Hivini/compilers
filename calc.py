# -----------------------------------------------------------------------------
# calc.py
#
# Simple Compler version yacc and lex
# -----------------------------------------------------------------------------

import sys
sys.path.insert(0, "../..")

tokens = (
    'NAME', 'INUMBER', 'FNUMBER'
)

literals = ['=', '+', '-', 'i', 'f', 'p']

# Tokens

t_NAME = r'[a-eg-hj-oq-z]'


def t_FNUMBER(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t


def t_INUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lexer = lex.lex()

# Parsing rules

precedence = (
    ('left', '+', '-'),
)

# dictionary of names
names = {}
abstract_tree = []

def p_statement_declareInt(p):
    'statement : "i" NAME'
    names[p[2]] = {"type": "INT", "value": None}

def p_statement_declareFloat(p):
    'statement : "f" NAME'
    names[p[2]] = {"type": "FLOAT", "value": None}

def p_statement_assign(p):
    'statement : NAME "=" expression'
    if p[1] not in names:
        raise Exception('Declare variable before using it.')
    if names[p[1]]['type'] == 'INT' and isinstance(p[3], float):
        raise Exception('Float cannot be assigned to type variable type int.')
    if names[p[1]]['type'] == 'FLOAT' and isinstance(p[3], int):
        names[p[1]]['value'] = float(p[3])
    else:
        names[p[1]]['value'] = p[3]


def p_statement_expr(p):
    '''statement : "p" expression'''
    print(p[2])


def p_expression_binop(p):
    '''expression : expression '+' expression
                  | expression '-' expression'''
    if p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]

def p_expression_inumber(p):
    "expression : INUMBER"
    p[0] = p[1]

def p_expression_fnumber(p):
    "expression : FNUMBER"
    p[0] = p[1]


def p_expression_name(p):
    "expression : NAME"
    try:
        p[0] = names[p[1]]['value']
        if p[0] == None:
            print('%s has not been assigned a value, default to 0.' % p[1])
            names[p[1]]['value'] = 0
            p[0] = 0
    except LookupError:
        print("Undefined name '%s'" % p[1])
        p[0] = 0


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")

import ply.yacc as yacc
parser = yacc.yacc()

file = open('code.txt')
s = file.readlines()
file.close()
for l in s:
    print(l)
    yacc.parse(l)

# Other flow, in case you want it.
# while True:
#     try:
#         s = input('calc > ')
#     except EOFError:
#         break
#     if not s:
#         continue
#     yacc.parse(s)
