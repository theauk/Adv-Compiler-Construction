import unittest

from parser import Parser, Error


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

    def test_with_paren(self):
        self.set_input('computation var i <- 10 - (2 * 3); i/2.')
        expected_result = ['2']
        result = self.parser.parse()
        self.assertEqual(result, expected_result)

    def test_with_multiple_vars(self):
        self.set_input('computation var i <- 2 * 3; var abracadabra <- 7; (((abracadabra * i))); i - 5 - 1 .')
        expected_result = ['42', '0']
        result = self.parser.parse()
        self.assertEqual(result, expected_result)

    def test_exceptions(self):
        self.set_input('computation 2 + notDefined;.')

        with self.assertRaises(Error) as context:
            self.parser.parse()

        expected_error_message = "SyntaxError: notDefined has not been defined"
        self.assertIn(expected_error_message, str(context.exception))


if __name__ == '__main__':
    unittest.main()
