from parser import Parser
from visualizer import Visualizer


def main():
    parser = Parser("tests/0_test.txt")
    parser.computation()

    visualizer = Visualizer(parser.blocks, parser.symbolTable, show_vars=True)
    text = visualizer.make_graph()
    print(text)


if __name__ == '__main__':
    main()
