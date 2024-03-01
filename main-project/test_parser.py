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
        parser = Parser('tests/if_redundant_phi.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/if_redundant_phi.dot')

        self.assertEqual(output_text, expected_output)

    def test_cse_while_do_not_cse_copied_var(self):
        parser = Parser('tests/cse_while_do_not_cse_copied_var.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/cse_while_do_not_cse_copied_var.dot')

        self.assertEqual(output_text, expected_output)

    def test_return_if_in_while_then_else_returns(self):
        parser = Parser('tests/return_if_in_while_then_else_returns.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/return_if_in_while_then_else_returns.dot')

        self.assertEqual(output_text, expected_output)

    def test_return_middle_of_while(self):
        parser = Parser('tests/return_middle_of_while.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/return_middle_of_while.dot')

        self.assertEqual(output_text, expected_output)

    def test_return_only_if(self):
        parser = Parser('tests/return_only_if.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/return_only_if.dot')

        self.assertEqual(output_text, expected_output)

    def test_return_only_else(self):
        parser = Parser('tests/return_only_else.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/return_only_else.dot')

        self.assertEqual(output_text, expected_output)

    # CLASS TESTS
    def test_fibonacci(self):
        parser = Parser('tests/class/fibonacci.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/class/fibonacci.dot')

        self.assertEqual(output_text, expected_output)


if __name__ == '__main__':
    unittest.main()
