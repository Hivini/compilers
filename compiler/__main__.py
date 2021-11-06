import argparse
import sys
import os

from .logger import Logger


def Run():
    # Create logger
    logger = Logger()

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file_path", help="Location of the file to compile, relative to current location.")
    args = parser.parse_args()
    file_path = args.file_path

    # Open file
    if not os.path.isfile(file_path):
        logger.LogError(f'{file_path} does not exist or is not a file.')
        sys.exit(1)
    try:
        f = open(file_path, 'r')
        program = f.read()
        print(program)
        f.close()
    except FileNotFoundError:
        logger.LogError(f'{file_path} could not be opened!')
        sys.exit(1)

    logger.LogSuccess('Successfully compiled!')


if __name__ == '__main__':
    Run()
