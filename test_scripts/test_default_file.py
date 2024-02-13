def get_default_fp():

    fp = open('./testfile.txt', 'w')

    fp.write('Car: mers\n')
    fp.write('Color: Black\n')

    default_fp = fp.tell()

    fp.close()

    return default_fp