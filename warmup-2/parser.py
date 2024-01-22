from tokenizer import Tokenizer
from tokens import TokenType


class Error(Exception):
    def __init__(self, name: str, desc: str):
        super().__init__(f"{name}: {desc}")
        self.name = name
        self.desc = desc


def parse():
    tokenizer = Tokenizer()
    first_inp = tokenizer.get_next_token()

    if first_inp != TokenType.COMPUTATION:
        raise Error("SyntaxError", f"expected computation but got {tokenizer.get_identifier(first_inp)}")


if __name__ == "__main__":
    parse()
