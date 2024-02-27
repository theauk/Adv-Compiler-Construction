from filereader import FileReader
from tokens import Tokens, Strings


class Tokenizer:
    def __init__(self, filename):
        self.my_file_reader = FileReader(filename)
        self.inp = self.my_file_reader.get_next()
        self.index_to_token_table = Tokens.get_index_to_id_dict()
        self.token_to_index_table = {}
        self.max_reserved_id = max(value for name, value in vars(Tokens).items() if isinstance(value, int))
        self.id_count = self.max_reserved_id + 1
        self.last_number = None
        self.last_id = ''
        self.DIGITS = '0123456789'

    def next_input(self) -> str:
        self.inp = self.my_file_reader.get_next()
        return self.inp

    def error(self, error_msg: str):
        self.my_file_reader.error(error_msg)

    def add_identifier(self, identifier: int) -> int:
        self.index_to_token_table[self.id_count] = identifier
        self.token_to_index_table[identifier] = self.id_count
        self.id_count += 1
        return self.id_count - 1

    def get_token_from_index(self, index: int) -> int:
        return self.index_to_token_table[index]

    def get_next_token(self):
        if not self.inp:
            return Tokens.EOF_TOKEN

        while self.inp.isspace():
            self.next_input()

        # Handle numbers
        if self.inp != '' and self.inp in self.DIGITS:
            res = int(self.inp)
            self.next_input()
            while self.inp != '' and self.inp in self.DIGITS:
                res = 10 * res + int(self.inp)
                self.next_input()
            self.last_number = int(res)
            return Tokens.NUMBER

        # Handle identifiers and reserved keywords
        elif self.inp.isalpha():
            res = self.inp
            self.next_input()
            while self.inp.isalnum():
                res += self.inp
                self.next_input()

            if res in Strings.KEYWORDS:  # Reserved keywords
                return Strings.KEYWORDS[res]
            elif res in self.token_to_index_table:  # Already seen id
                self.last_id = res
                return self.token_to_index_table[res]
            else:  # New id
                self.last_id = res
                return self.add_identifier(res)

        # Handle symbols
        elif self.inp != '':
            cur_inp = self.inp
            self.next_input()
            combined_inp = cur_inp + self.inp

            if combined_inp in Strings.SYMBOLS:
                self.next_input()
                return Strings.SYMBOLS[combined_inp]
            elif cur_inp in Strings.SYMBOLS:
                return Strings.SYMBOLS[cur_inp]
            else:
                return Tokens.ERROR_TOKEN

        else:
            return Tokens.EOF_TOKEN
