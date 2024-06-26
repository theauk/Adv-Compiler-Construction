from reader import Reader
from tokens import TokenType


class Tokenizer:
    def __init__(self):
        self.reader = Reader()

        self.indexToEnumTable = TokenType.get_index_to_enum_dict()
        self.indexToTokenTable = {}
        self.tokenToIndexTable = {}
        self.maxReservedId = max(value for name, value in vars(TokenType).items() if isinstance(value, int))
        self.idCount = self.maxReservedId + 1
        self.DIGITS = '0123456789'

        self.lastNumber = ''
        self.lastIdentifier = ''

        self.inp = ''

    def start_reader(self):
        self.reader.start()
        self.get_next_inp()

    def get_next_inp(self):
        self.inp = self.reader.get_next_inp()

    def add_identifier(self, identifier):
        self.indexToTokenTable[self.idCount] = identifier
        self.tokenToIndexTable[identifier] = self.idCount
        self.idCount += 1
        return self.idCount - 1

    def get_identifier(self, index):
        if index in self.indexToTokenTable:
            return self.indexToTokenTable[index]
        else:
            return self.indexToEnumTable[index]

    def get_next_token(self):
        if not self.inp:
            return TokenType.EOF

        while self.inp.isspace():
            self.get_next_inp()

        # Handle numbers
        if self.inp != '' and self.inp in self.DIGITS:
            res = int(self.inp)
            self.get_next_inp()
            while self.inp != '' and self.inp in self.DIGITS:
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

            if res in TokenType.KEYWORDS:  # Reserved keywords
                return TokenType.KEYWORDS[res]
            elif res in self.tokenToIndexTable:
                self.lastIdentifier = res  # Already seen id
                return self.tokenToIndexTable[res]
            else:
                self.lastIdentifier = res  # New id
                return self.add_identifier(res)

        # Handle symbols
        elif self.inp != '':
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

        else:
            return TokenType.EOF
