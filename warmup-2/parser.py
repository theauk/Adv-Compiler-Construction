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
        self.token = None
        self.symbolTable = {}
        self.results = []

    def start_tokenizer(self):
        self.tokenizer.start_reader()
        self.get_next_token()

    def get_next_token(self):
        self.token = self.tokenizer.get_next_token()

    def parse(self):
        self.computation()
        return self.results

    def computation(self):
        if self.token != TokenType.COMPUTATION:
            raise Error("SyntaxError", f"expected computation got {self.tokenizer.get_identifier(self.token)}")
        else:
            self.get_next_token()

            while self.token == TokenType.VAR:
                self.get_next_token()
                self.assignment()

            result = 0

            while True:
                result = self.expression()

                if self.token != TokenType.PERIOD and self.token != TokenType.SEMICOLON:
                    raise Error("SyntaxError", f"expected . or ; got {self.tokenizer.get_identifier(self.token)}")

                self.results.append(str(int(result)) if result == int(result) else str(result))
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

        while self.token == TokenType.TIMES or self.token == TokenType.DIVISION:
            if self.token == TokenType.TIMES:
                self.get_next_token()
                result *= self.factor()
            elif self.token == TokenType.DIVISION:
                self.get_next_token()
                result /= self.factor()

        return result

    def factor(self):
        result = 0

        if self.token > self.tokenizer.maxReservedId:
            current_token = self.token
            self.get_next_token()
            return self.symbolTable[current_token]

        elif self.token == TokenType.NUMBER:
            current_number = self.tokenizer.lastNumber
            self.get_next_token()
            return current_number

        elif self.token == TokenType.OPEN_PARENTHESIS:
            self.get_next_token()
            result = self.expression()
            if self.token != TokenType.CLOSE_PARENTHESIS:
                raise Error("SyntaxError", f"expected ) got {self.tokenizer.get_identifier(self.token)}")
            self.get_next_token()

        else:
            raise Error("SyntaxError",
                        f"expected ( or number or identifier got {self.tokenizer.get_identifier(self.token)}")

        return result


if __name__ == "__main__":
    parser = Parser()
    parser.start_tokenizer()  # to avoid unit tests hanging for input()
    res = parser.parse()
    print(*res, sep='\n')
