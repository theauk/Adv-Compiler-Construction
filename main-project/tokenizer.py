from filereader import FileReader
from tokens import Tokens


class Tokenizer:
    def __init__(self, filename):
        self.my_file_reader = FileReader(filename)
        self.input_sym = self.my_file_reader.get_next()

        self.index_to_token_table = Tokens.get_index_to_id_dict()
        self.token_to_index_table = {}
        self.max_reserved_id = max(value for name, value in vars(Tokens).items() if isinstance(value, int))
        self.id_count = self.max_reserved_id + 1

        self.last_number = ''
        self.last_id = ''

        self.DIGITS = '0123456789'

    def next_input(self):
        self.input_sym = self.my_file_reader.get_next()

    def error(self, error_msg):
        self.my_file_reader.error(error_msg)

    def add_identifier(self, identifier):
        self.index_to_token_table[self.id_count] = identifier
        self.token_to_index_table[identifier] = self.id_count
        self.id_count += 1
        return self.id_count - 1

    def get_identifier(self, index):
        return self.index_to_token_table[index]

    def get_next_token(self):
        if not self.input_sym:
            return Tokens.EOF_TOKEN

        while self.input_sym.isspace():
            self.next_input()

            # Handle numbers
            if self.input_sym != '' and self.input_sym in self.DIGITS:
                res = int(self.input_sym)
                self.next_input()
                while self.input_sym != '' and self.input_sym in self.DIGITS:
                    res = 10 * res + int(self.input_sym)
                    self.next_input()
                self.last_number = res
                return Tokens.NUMBER


            # TODO: færdiggør parseren ved at udvide det du havde før men tilføje det der mangler fra det nye sprog
            # TODO: start opg. 1 frontend parten ved at finde ud af hvordan du vil holde infoen (og tænk over grafopgaven samtidig)

