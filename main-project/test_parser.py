import unittest

from parser import Parser
from visualizer import Visualizer


def read_expected_output(filename):
    try:
        with open(filename, 'r') as file:
            file_contents = file.read()
            return file_contents

    except Exception as e:
        print(f"An error occurred: {e}")


def write_to_file(filename, contents):
    file_path = filename

    try:
        with open(file_path, 'w') as file:
            file.write(contents)

    except Exception as e:
        print(f"An error occurred: {e}")


class TestInterpreter(unittest.TestCase):

    def test_print_test_dot_graph(self):
        parser = Parser('tests/0_test.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        text = visualizer.make_graph()
        write_to_file('tests/0_test.dot', text)
        print(text)

    def test_redundant_phi_if(self):
        expected_output = read_expected_output('tests/redundant_phi_if.dot')

        parser = Parser('tests/redundant_phi_if.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph().strip()

        self.assertEquals(output_text, expected_output)


if __name__ == '__main__':
    unittest.main()
