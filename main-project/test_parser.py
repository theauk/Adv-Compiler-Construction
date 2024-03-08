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
        parser = Parser('tests/my_tests/if_redundant_phi.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/my_tests/if_redundant_phi.dot')

        self.assertEqual(output_text, expected_output)

    def test_cse_while_do_not_cse_copied_var(self):
        parser = Parser('tests/my_tests/cse_while_do_not_cse_copied_var.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/my_tests/cse_while_do_not_cse_copied_var.dot')

        self.assertEqual(output_text, expected_output)

    def test_return_if_in_while_then_else_returns(self):
        parser = Parser('tests/my_tests/return_if_in_while_then_else_returns.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/my_tests/return_if_in_while_then_else_returns.dot')

        self.assertEqual(output_text, expected_output)

    def test_return_middle_of_while(self):
        parser = Parser('tests/my_tests/return_middle_of_while.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/my_tests/return_middle_of_while.dot')

        self.assertEqual(output_text, expected_output)

    def test_return_only_if(self):
        parser = Parser('tests/my_tests/return_only_if.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/my_tests/return_only_if.dot')

        self.assertEqual(output_text, expected_output)

    def test_return_only_else(self):
        parser = Parser('tests/my_tests/return_only_else.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/my_tests/return_only_else.dot')

        self.assertEqual(output_text, expected_output)

    def test_unassigned_var_assigned_only_in_then(self):
        parser = Parser('tests/my_tests/unassigned_var_assigned_only_in_then.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/my_tests/unassigned_var_assigned_only_in_then.dot')

        self.assertEqual(output_text, expected_output)

    def test_uninitialized_var_in_then_else(self):
        parser = Parser('tests/my_tests/uninitialized_var_in_then_else.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/my_tests/uninitialized_var_in_then_else.dot')

        self.assertEqual(output_text, expected_output)

    def test_unassigned_var_assigned_in_while(self):
        parser = Parser('tests/my_tests/unassigned_var_assigned_in_while.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/my_tests/unassigned_var_assigned_in_while.dot')

        self.assertEqual(output_text, expected_output)

    def test_if_sequential_ifs_in_if(self):
        parser = Parser('tests/my_tests/if_sequential_ifs_in_if.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/my_tests/if_sequential_ifs_in_if.dot')

        self.assertEqual(output_text, expected_output)

    def test_array_i_j_not_read(self):
        parser = Parser('tests/my_tests/array_i_j_not_read.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/my_tests/array_i_j_not_read.dot')

        self.assertEqual(output_text, expected_output)

    def test_array_i_j_read(self):
        parser = Parser('tests/my_tests/array_i_j_read.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/my_tests/array_i_j_read.dot')

        self.assertEqual(output_text, expected_output)

    def test_array_i_not_j_read(self):
        parser = Parser('tests/my_tests/array_i_not_j_read.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/my_tests/array_i_not_j_read.dot')

        self.assertEqual(output_text, expected_output)

    def test_array_i_read_j_not(self):
        parser = Parser('tests/my_tests/array_i_read_j_not.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/my_tests/array_i_read_j_not.dot')

        self.assertEqual(output_text, expected_output)

    # CLASS TESTS -------------------------------------
    def test_complex_while(self):
        parser = Parser('tests/class_tests/complex_while.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/class_tests/complex_while.dot')

        self.assertEqual(output_text, expected_output)

    def test_fibonacci(self):
        parser = Parser('tests/class_tests/fibonacci.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/class_tests/fibonacci.dot')

        self.assertEqual(output_text, expected_output)

    def test_NestedWhileIf(self):
        parser = Parser('tests/class_tests/NestedWhileIf.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/class_tests/NestedWhileIf.dot')

        self.assertEqual(output_text, expected_output)

    def test_no_array_load(self):
        parser = Parser('tests/class_tests/no_array_load.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/class_tests/no_array_load.dot')

        self.assertEqual(output_text, expected_output)

    def test_no_phis_xy(self):
        parser = Parser('tests/class_tests/no_phis_x=y.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/class_tests/no_phis_x=y.dot')

        self.assertEqual(output_text, expected_output)

    def test_prefix_sum(self):
        parser = Parser('tests/class_tests/prefix_sum.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/class_tests/prefix_sum.dot')

        self.assertEqual(output_text, expected_output)

    def test_RedundantLoad(self):
        parser = Parser('tests/class_tests/RedundantLoad.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True, show_instr_vars=False)
        output_text = visualizer.make_graph()

        expected_output = read_expected_output('tests/class_tests/RedundantLoad.dot')

        self.assertEqual(output_text, expected_output)


if __name__ == '__main__':
    unittest.main()
