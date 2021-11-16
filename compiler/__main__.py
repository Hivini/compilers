import argparse
import sys
import os
from compiler.lexer import Lexer

from compiler.logger import Logger
from compiler.parser_2 import Parser, ParserError


def PrintAST(logger, current, depth):
    spaces = '\t'*depth
    logger.LogDebug(f'{spaces}-{current.type.name}')
    if current.lineno != None:
        logger.LogDebug(f'{spaces}| line no. {current.lineno}')
    if current.variableType != None:
        logger.LogDebug(f'{spaces}| {current.variableType}')
    if current.variableName != None:
        logger.LogDebug(f'{spaces}| {current.variableName}')
    if current.variableValue != None:
        logger.LogDebug(f'{spaces}| {current.variableValue}')
    for c in current.children:
        PrintAST(logger, c, depth+1)


def Run():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file_path", help="Location of the file to compile, relative to current location.")
    parser.add_argument(
        "-v", "--verbose", help="Add output prints to show debug elements.", action="store_true")
    args = parser.parse_args()
    file_path = args.file_path

    # Create logger
    logger = Logger(args.verbose)

    # Open file
    if not os.path.isfile(file_path):
        logger.LogError(f'{file_path} does not exist or is not a file.')
        sys.exit(1)
    try:
        f = open(file_path, 'r')
        program = f.read()
        lines = program.splitlines()
        f.close()
    except FileNotFoundError:
        logger.LogError(f'{file_path} could not be opened!')
        sys.exit(1)

    lexerInstance = Lexer()
    lexer = lexerInstance.createLexer()
    lexer.input(program)
    while True:
        tok = lexer.token()
        if lexerInstance.n_errors != 0:
            errorMessage = f'Invalid token \'{lexerInstance.errorToken}\' at line {lexerInstance.errorLine}'
            errorLine = lines[lexerInstance.errorLine]
            logger.LogError(f'{errorMessage}:\n\t{errorLine}')
            sys.exit(1)
        if not tok:
            break

    parserInstance = Parser(lines)
    try:
        root = parserInstance.parseProgram(program)
        if (args.verbose):
            PrintAST(logger, root, 0)
        logger.LogDebug('Symbol Table:')
        logger.LogDebug(parserInstance.names)
        logger.LogSuccess('Successfully compiled!')
    except ParserError:
        logger.LogError(parserInstance.first_error)


if __name__ == '__main__':
    Run()
