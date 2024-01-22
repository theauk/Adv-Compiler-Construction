from reader import Reader
from tokens import TokenType


class Tokenizer:  # TODO: comment out vars not in the simpler warm up language
    def __init__(self, debug=False):
        self.debug = debug
        self.reader = Reader()

        self.tokensToIndexTable = {
            'number': TokenType.NUMBER,
            'identifier': TokenType.IDENTIFIER,

            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.TIMES,
            '/': TokenType.DIVISION,

            '==': TokenType.EQUAL,
            '!=': TokenType.NOT_EQUAL,
            '<': TokenType.LESS_THAN,
            '>': TokenType.GREATER_THAN,
            '<=': TokenType.LESS_THAN_OR_EQUAL,
            '>=': TokenType.GREATER_THAN_OR_EQUAL,

            '.': TokenType.PERIOD,
            ',': TokenType.COMMA,
            ';': TokenType.SEMICOLON,

            '(': TokenType.OPEN_PARENTHESIS,
            ')': TokenType.CLOSE_PARENTHESIS,
            '[': TokenType.OPEN_BRACKET,
            ']': TokenType.CLOSE_BRACKET,

            'let': TokenType.LET,
            'call': TokenType.CALL,

            'if': TokenType.IF,
            'then': TokenType.THEN,
            'else': TokenType.ELSE,
            'fi': TokenType.FI,

            'while': TokenType.WHILE,
            'do': TokenType.DO,
            'od': TokenType.OD,

            'return': TokenType.RETURN,

            'variable': TokenType.VAR,
            'array': TokenType.ARRAY,
            'void': TokenType.VOID,
            'function': TokenType.FUNCTION,
            'main': TokenType.MAIN,

            '<-': TokenType.ASSIGN,
            'computation': TokenType.COMPUTATION
        }

        self.indexToTokenTable = {value: key for key, value in self.tokensToIndexTable}  # associate number with its corresponding string
        self.idCount = max(self.indexToTokenTable.values()) + 1
        self.KEYWORDS = ['computation', 'var']
        self.SYMBOLS = ['+', '-', '*', '/', '(', ')', ';', '.']
        self.DIGITS = "0123456789"

        self.lastNumber = ''
        self.lastIdentifier = ''

        self.inp = ''
        self.get_next_inp()

    def get_next_inp(self):
        self.inp = self.reader.get_next_inp()

    def add_identifier(self, identifier):
        self.tokensToIndexTable[identifier] = self.idCount
        self.indexToTokenTable[self.idCount] = identifier
        self.idCount += 1

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

            if res not in self.KEYWORDS:
                self.add_identifier(res)
            return self.tokensToIndexTable[res]

        # Handle symbols






