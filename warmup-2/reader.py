import sys


class Reader:
    def __init__(self):
        self.stdin = sys.stdin

    def get_next_inp(self):
        return self.stdin.read(1)

    def close(self):
        self.stdin.close()
