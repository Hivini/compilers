import argparse
import sys
import os

def run():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file_path", help="Location of the file to compile, relative to current location.")
    args = parser.parse_args()
    file_path = args.file_path
    # Open file
    if not os.path.isfile(file_path):    
        print(f'{file_path} does not exist or is not a file.')
        sys.exit(1)
    try:
        f = open(file_path, 'r')
        program = f.read()
        print(program)
        f.close()
    except FileNotFoundError:
        print(f'{file_path} could not be opened!')
        sys.exit(1)


if __name__ == '__main__':
    run()
