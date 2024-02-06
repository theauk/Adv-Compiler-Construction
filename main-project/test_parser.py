import unittest

from parser import Parser


class TestInterpreter(unittest.TestCase):

    def test_something(self):
        parser = Parser('test.txt')
        parser.computation()
        print("test")


if __name__ == '__main__':
    unittest.main()
