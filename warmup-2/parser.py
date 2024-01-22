from tokenizer import Tokenizer
from tokens import TokenType


class Error(Exception):
    def __init__(self, name: str, desc: str):
        super().__init__(f"{name}: {desc}")
        self.name = name
        self.desc = desc


def parse():
    tokenizer = Tokenizer()
    inp = tokenizer.get_next_token()

    if inp != TokenType.COMPUTATION:
        raise Error("SyntaxError", f"expected computation but got {tokenizer.get_identifier(inp)}")

    while inp != TokenType.EOF:
        inp = tokenizer.get_next_token()
        print(inp)

    #tokenizer.close_reader()


if __name__ == "__main__":
    parse()
