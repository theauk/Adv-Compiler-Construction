import unittest

from parser import Parser
from visualizer import Visualizer


class TestInterpreter(unittest.TestCase):

    def test_something(self):
        parser = Parser('test.txt')
        parser.computation()

        visualizer = Visualizer(parser.blocks)
        text = visualizer.make_graph()
        print(text)


if __name__ == '__main__':
    unittest.main()
