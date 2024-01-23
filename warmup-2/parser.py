from tokenizer import Tokenizer
from tokens import TokenType


class Error(Exception):
    def __init__(self, name: str, desc: str):
        super().__init__(f"{name}: {desc}")
        self.name = name
        self.desc = desc


class Parser:
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.token = self.tokenizer.get_next_token()
        self.symbolTable = {}

    def get_next_token(self):
        self.token = self.tokenizer.get_next_token()

    def parse(self):
        self.computation()

    def computation(self):
        if self.token != TokenType.COMPUTATION:
            raise Error("SyntaxError", f"expected computation got {self.tokenizer.get_identifier(self.token)}")
        else:
            self.get_next_token()

            while self.token == TokenType.VAR:
                self.assignment()
                self.get_next_token()

            result = 0

            while True:
                result = self.expression()

                if self.token != TokenType.PERIOD and self.token != TokenType.SEMICOLON:
                    raise Error("SyntaxError", f"expected . or ; got {self.tokenizer.get_identifier(self.token)}")

                print(result)
                if self.token == TokenType.PERIOD:
                    break
                elif self.token == TokenType.SEMICOLON:
                    self.get_next_token()

    def assignment(self):
        if self.token <= self.tokenizer.maxReservedId:
            raise Error("SyntaxError", f"expected identifier got {self.tokenizer.get_identifier(self.token)}")

        identifier = self.token
        self.get_next_token()

        if self.token != TokenType.ASSIGN:
            raise Error("SyntaxError", f"expected <- got {self.tokenizer.get_identifier(self.token)}")
        self.get_next_token()

        expression = self.expression()

        self.symbolTable[identifier] = expression
        self.get_next_token()

        if self.token != TokenType.SEMICOLON:
            raise Error("SyntaxError", f"expected ; got {self.tokenizer.get_identifier(self.token)}")
        self.get_next_token()

    def expression(self):
        result = self.term()

        while self.token == TokenType.PLUS or self.token == TokenType.MINUS:
            if self.token == TokenType.PLUS:
                self.get_next_token()
                result += self.term()
            elif self.token == TokenType.MINUS:
                self.get_next_token()
                result -= self.term()

        return result

    def term(self):
        result = self.factor()
        self.get_next_token()

        while self.token == TokenType.TIMES or self.token == TokenType.DIVISION:
            if self.token == TokenType.TIMES:
                result *= self.factor()
                self.get_next_token()
            elif self.token == TokenType.DIVISION:
                result /= self.factor()
                self.get_next_token()

        return result

    def factor(self):
        result = 0

        if self.token > self.tokenizer.maxReservedId:
            return self.symbolTable[self.token]

        elif self.token == TokenType.NUMBER:
            return self.tokenizer.lastNumber

        elif self.token == TokenType.OPEN_PARENTHESIS:
            self.get_next_token()
            result = self.expression()
            if self.token != TokenType.CLOSE_PARENTHESIS:
                raise Error("SyntaxError", f"expected ) got {self.tokenizer.get_identifier(self.token)}")

        else:
            raise Error("SyntaxError",
                        f"expected ( or number or identifier got {self.tokenizer.get_identifier(self.token)}")

        return result


if __name__ == "__main__":
    parser = Parser()
    parser.parse()
