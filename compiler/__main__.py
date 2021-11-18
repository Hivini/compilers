import argparse
import sys
import os
from compiler.lexer import Lexer

from compiler.logger import Logger
from compiler.parser import Parser, ParserError
from compiler.semantics import SemanticAnalyzer, SemanticError
from compiler.tac import TACProcessor


def PrintAST(logger, current, depth):
    spaces = '\t'*depth
    logger.LogDebug(f'{spaces}-{current.type.name}')
    if current.variableType != None:
        logger.LogDebug(f'{spaces}| Type: {current.variableType}')
    if current.variableName != None:
        logger.LogDebug(f'{spaces}| Name: {current.variableName}')
    if current.variableValue != None:
        logger.LogDebug(f'{spaces}| Value: {current.variableValue}')
    for c in current.children:
        PrintAST(logger, c, depth+1)


def PrintSymbolTable(logger, current, depth):
    spaces = '\t'*depth
    logger.LogDebug(f'{spaces}-{current.table}')
    for c in current.children:
        PrintSymbolTable(logger, c, depth+1)


def Run():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file_path", help="Location of the file to compile, relative to current location.")
    parser.add_argument(
        "-v", "--verbose", help="Add output prints to show debug elements.", action="store_true")
    parser.add_argument(
        "-tac", "--tacprint", help="Outputs the TAC as a print instead of a file.", action="store_true")
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
            logger.LogDebug('Symbol Tables:')
            PrintSymbolTable(logger, parserInstance.symbolTable, 0)
        semanticInstance = SemanticAnalyzer(root, lines)
        semanticInstance.checkSemantics()
        if (args.verbose):
            logger.LogDebug('AST after semantics:')
            PrintAST(logger, root, 0)
            logger.LogDebug('Symbol Tables after semantics:')
            PrintSymbolTable(logger, parserInstance.symbolTable, 0)
        tacProcessor = TACProcessor(root)
        taclines = tacProcessor.generateTAC()
        if (args.tacprint):
            tacBanner = '=' * 10
            logger.LogDebug(f'{tacBanner} TAC {tacBanner}')
            i = 1
            for line in taclines:
                logger.LogDebug(f'{i})\t{line}')
                i += 1
        else:
            try:
                filename = file_path.split('.')[0]
                f = open(f'{filename}.output', 'w')
                # We add the end of line first so the writelines functions
                # handle end of line character for us based on the OS.
                for i in range(len(taclines)):
                    taclines[i] = taclines[i] + '\n'
                f.writelines(taclines)
                f.close()
            except:
                logger.LogError('Error ocurred when writing the file')
                sys.exit(1)
        logger.LogSuccess('Successfully compiled!')
    except ParserError:
        logger.LogError(parserInstance.first_error)
    except SemanticError:
        logger.LogError(semanticInstance.error)


if __name__ == '__main__':
    Run()
