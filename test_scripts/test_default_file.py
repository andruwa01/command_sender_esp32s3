
default_file_path = './satellites/testfile.txt'

def initialize_default_file():

    fp = open(default_file_path, 'w')

    fp.write('Car: mers\n')
    fp.write('Color: Black\n')

    default_fp = fp.tell()

    fp.close()