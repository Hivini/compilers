import argparse
import sys
import os

from compiler.logger import Logger
from compiler.lexer import Lexer


def Run():
    # Create logger
    logger = Logger()

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file_path", help="Location of the file to compile, relative to current location.")
    args = parser.parse_args()
    file_path = args.file_path

    lexerInstance = Lexer()
    lexer = lexerInstance.createLexer()

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

    lexer.input(program)
    while True:
        tok = lexer.token()
        if not tok:
            break
        if lexerInstance.n_errors != 0:
            errorMessage = f'Invalid token \'{lexerInstance.errorToken}\' at line {lexerInstance.errorLine}'
            errorLine = lines[lexerInstance.errorLine]
            logger.LogError(f'{errorMessage}:\n\t{errorLine}')
            sys.exit(1)
    logger.LogSuccess('Successfully compiled!')


if __name__ == '__main__':
    Run()
