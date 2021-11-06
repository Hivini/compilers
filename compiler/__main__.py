import os

FILE_NAME = 'code2.txt'

def run():
    if (os.path.isfile(FILE_NAME)):    
        try:
            f = open(FILE_NAME, 'r')
            program = f.read()
            print(program)
            f.close()
        except FileNotFoundError:
            print('File could not be opened!')
    else:
        print(f'{FILE_NAME} does not exist or is not a file.')


if __name__ == '__main__':
    run()
