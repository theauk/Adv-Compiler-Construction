import unittest

import interpreter


class TestInterpreter(unittest.TestCase):

    def test_ints(self):
        result = interpreter.main("2+3.5*4.9-10.788.")
        self.assertEqual(result, ["5", "20", "-1", "788"])

    def test_floats(self):
        result = interpreter.main("5/2.10/8.")
        self.assertEqual(result, ["2.5", "1.25"])

    def test_space(self):
        result = interpreter.main("2 +  3. 5*   4 .")
        self.assertEqual(result, ["5", "20"])

    def test_paren(self):
        result = interpreter.main("1+2-(4*2)+(3+3).")
        self.assertEqual(result, ["1"])

        result = interpreter.main("1+(4*2)*(3+3)+5.")
        self.assertEqual(result, ["54"])

        result = interpreter.main("(07-(6*02)-95)+77.")
        self.assertEqual(result, ["-23"])

    def test_exceptions(self):
        result = interpreter.main("2+2a.")
        self.assertEqual(result, ["SyntaxError: Invalid character"])

        result = interpreter.main("2+2")
        self.assertEqual(result, ["SyntaxError: Missing end period"])

        result = interpreter.main("(2+2.")
        self.assertEqual(result, ["SyntaxError: Unclosed parenthesis"])

        result = interpreter.main("2+2).")
        self.assertEqual(result, ["SyntaxError: Invalid character"])


if __name__ == '__main__':
    unittest.main()
