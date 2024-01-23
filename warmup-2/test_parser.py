import unittest

from parser import Parser


class TestInterpreter(unittest.TestCase):

    def setUp(self):
        self.parser = Parser()

    def set_input(self, input_string):
        self.parser.tokenizer.reader.text = input_string
        self.parser.tokenizer.get_next_inp()
        self.parser.get_next_token()

    def test_numeric_input(self):
        self.set_input('computation 1 + 2; 4.')
        expected_result = ['3', '4']
        result = self.parser.parse()
        self.assertEqual(result, expected_result)

    def test_with_one_var(self):
        self.set_input('computation var i <- 1 + 2; i + 1.')
        expected_result = ['4']
        result = self.parser.parse()
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
