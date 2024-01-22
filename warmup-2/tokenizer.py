from reader import Reader
from tokens import TokenType


class Tokenizer:  # TODO: comment out vars not in the simpler warm up language
    def __init__(self, debug=False):
        self.debug = debug
        self.reader = Reader()

        self.indexToTokenTable = {}
        self.idCount = max(value for name, value in vars(TokenType).items() if isinstance(value, int)) + 1
        self.DIGITS = "0123456789"

        self.lastNumber = ''
        self.lastIdentifier = ''

        self.inp = ''
        self.get_next_inp()

    def get_next_inp(self):
        self.inp = self.reader.get_next_inp()

    def add_identifier(self, identifier):
        self.indexToTokenTable[self.idCount] = identifier
        self.idCount += 1
        return self.idCount - 1

    def get_next_token(self):

        if not self.inp:
            return TokenType.EOF

        while self.inp.isspace():
            self.get_next_inp()

        # Handle numbers
        if self.inp in self.DIGITS:
            res = int(self.inp)
            self.get_next_inp()
            while self.inp in self.DIGITS:
                res = 10 * res + int(self.inp)
                self.get_next_inp()
            self.lastNumber = res
            return TokenType.NUMBER

        # Handle identifiers and reserved keywords
        elif self.inp.isalpha():
            res = self.inp
            self.get_next_inp()
            while self.inp.isalnum():
                res += self.inp
                self.get_next_inp()

            if res in TokenType.KEYWORDS:
                return TokenType.KEYWORDS[res]
            else:
                index = self.add_identifier(res)
                return self.indexToTokenTable[index]

        # Handle symbols
        else:
            cur_inp = self.inp
            self.get_next_inp()
            combined_inp = cur_inp + self.inp

            if combined_inp in TokenType.SYMBOLS:
                self.get_next_inp()
                return TokenType.SYMBOLS[combined_inp]
            elif cur_inp in TokenType.SYMBOLS:
                return TokenType.SYMBOLS[cur_inp]
            else:
                return TokenType.INVALID








