import os

try:
    f = open('synchronizer/tests/exceptions/test_file.txt')
    a = 10 / 0
except FileNotFoundError as error:
    print(error)
except Exception as error:
    print(error)
else:
    print(f.read())
    f.close()
finally:
    print('Executing finally.')