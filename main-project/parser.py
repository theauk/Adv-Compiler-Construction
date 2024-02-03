from tokenizer import Tokenizer
from tokens import Tokens


class Parser:
    def __init__(self, file_name):
        self.tokenizer = Tokenizer(file_name)
        self.token: int = 0
        self.symbolTable = {}
        self.next_token()

    def next_token(self):
        self.token = self.tokenizer.get_next_token()

    def check_identifier(self):
        if self.token != Tokens.IDENT:
            self.tokenizer.error(
                f"SyntaxError: expected ident got {self.tokenizer.get_token_from_index(self.token)}")
            return False
        elif self.token <= self.tokenizer.max_reserved_id:
            self.tokenizer.error(
                f"SyntaxError: got the reserved keyword {self.tokenizer.get_token_from_index(self.token)}")
            return False
        else:
            self.next_token()
            return True

    def check_token(self, token_type):
        if self.token != token_type:
            self.tokenizer.error(
                f"SyntaxError: expected {self.tokenizer.get_token_from_index(token_type)} got {self.tokenizer.get_token_from_index(self.token)}")
            return False
        else:
            self.next_token()
            return True

    def computation(self):
        result = ''

        if self.check_token(Tokens.MAIN_TOKEN):
            self.next_token()

            # { varDecl } which starts with typeDecl starting with either "var" or "array"
            while self.token == Tokens.VAR_TOKEN or self.token == Tokens.ARR_TOKEN:
                self.next_token()
                result += self.var_declaration()

            # { funcDecl } -> [ "void" ] "function"...
            while self.token == Tokens.VOID_TOKEN or self.token == Tokens.FUNC_TOKEN:
                self.next_token()
                if self.token == Tokens.FUNC_TOKEN:
                    self.next_token()
                result += self.func_declaration()

            # "{" statSequence
            check_end_token = False
            while self.token == Tokens.BEGIN_TOKEN:
                self.next_token()
                result += self.stat_sequence()
                check_end_token = True

            if check_end_token:
                # "}"
                self.check_token(Tokens.END_TOKEN)

            # final "."
            self.check_token(Tokens.PERIOD_TOKEN)

        return 'COMPUTATION ' + result

    def var_declaration(self):
        result = ''
        # Handle arrays
        if self.token == Tokens.OPEN_BRACKET_TOKEN:
            self.next_token()
            result += self.array_declaration()

        # Check if valid ident
        self.check_identifier()

        # Check for additional idents seperated by ","
        while self.token == Tokens.COMMA_TOKEN:
            self.check_identifier()

        # Check for ";"
        self.check_token(Tokens.SEMI_TOKEN)

        return 'VAR_DECLARATION ' + result

    def array_declaration(self):
        result = ''
        # "["
        while self.check_token(Tokens.OPEN_BRACKET_TOKEN):
            # number
            self.check_token(Tokens.NUMBER)
            # "]"
            self.check_token(Tokens.CLOSE_BRACKET_TOKEN)

        return 'ARRAY_DECLARATION '

    def func_declaration(self):
        result = ''
        # Check if valid ident
        self.check_identifier()
        # formalParam
        result += self.formal_parameter()
        # Check for ";"
        self.check_token(Tokens.SEMI_TOKEN)
        # funcBody
        result += self.func_body()
        # Check for ";"
        self.check_token(Tokens.SEMI_TOKEN)

        return 'FUNC_DECLARATION ' + result

    def formal_parameter(self):
        result = ''
        # Check for "("
        self.check_token(Tokens.OPEN_PAREN_TOKEN)
        # Check for optional ident
        if self.token == Tokens.IDENT:
            self.check_identifier()
            # Check for additional parameters
            while self.token == Tokens.COMMA_TOKEN:
                self.next_token()
                self.check_identifier()
        # Check for ")"
        self.check_token(Tokens.CLOSE_PAREN_TOKEN)
        return 'FORMAL_PARAMETER ' + result

    def func_body(self):
        result = ''
        # { varDecl } which starts with typeDecl starting with either "var" or "array"
        while self.token == Tokens.VAR_TOKEN or self.token == Tokens.ARR_TOKEN:
            self.next_token()
            result += self.var_declaration()

        # Check for "{"
        self.check_token(Tokens.BEGIN_TOKEN)
        # Check for optional statSequence
        result += self.stat_sequence()
        # Check for "}"
        self.check_token(Tokens.END_TOKEN)

        return 'FUNC_BODY ' + result

    def stat_sequence(self):
        result = ''
        # statement
        result += self.statement()
        # Check for additional statements
        while self.token == Tokens.SEMI_TOKEN:
            self.next_token()
            result += self.statement()

        return 'STAT_SEQUENCE ' + result

    def statement(self):
        result = ''
        if self.token == Tokens.LET_TOKEN:
            self.next_token()
            result += self.assignment()
        elif self.token == Tokens.FUNC_TOKEN:
            self.next_token()
            result += self.func_call()
        elif self.token == Tokens.IF_TOKEN:
            self.next_token()
            result += self.if_statement()
        elif self.token == Tokens.WHILE_TOKEN:
            self.next_token()
            result += self.while_statement()
        elif self.token == Tokens.RETURN_TOKEN:
            self.next_token()
            result += self.return_statement()

        return 'STATEMENT ' + result

    def assignment(self):  # TODO update symbol table
        result = ''
        result += self.designator()
        # "<-"
        self.check_token(Tokens.BECOMES_TOKEN)
        result += self.expression()
        return 'ASSIGNMENT ' + result

    def func_call(self):
        result = ''

        self.check_identifier()

        if self.check_token(Tokens.OPEN_PAREN_TOKEN):
            result += self.expression()
            while self.token == Tokens.COMMA_TOKEN:
                self.next_token()
                result += self.expression()
            self.check_token(Tokens.CLOSE_PAREN_TOKEN)

        return 'FUNC_CALL ' + result

    def if_statement(self):
        result = ''

        result += self.relation()
        self.check_token(Tokens.THEN_TOKEN)
        result += self.stat_sequence()

        if self.token == Tokens.ELSE_TOKEN:
            self.next_token()
            result += self.stat_sequence()

        self.check_token(Tokens.FI_TOKEN)
        return 'IF_STATEMENT ' + result

    def while_statement(self):
        result = ''
        result += self.relation()
        self.check_token(Tokens.DO_TOKEN)
        result += self.stat_sequence()
        self.check_token(Tokens.OD_TOKEN)

    def return_statement(self):
        result = ''
        result += self.expression()
        return 'RETURN_STATEMENT ' + result

    def designator(self):
        result = ''
        self.check_identifier()
        while self.token == Tokens.OPEN_BRACKET_TOKEN:
            self.next_token()
            result += self.expression()
            self.check_token(Tokens.CLOSE_BRACKET_TOKEN)
        return 'DESIGNATOR ' + result

    def expression(self):  # TODO else clause should return nothing FOR sel.return [] can be blank
        result = ''
        result += self.term()

        while self.token == Tokens.PLUS_TOKEN or self.token == Tokens.MINUS_TOKEN:
            if self.token == Tokens.PLUS_TOKEN:
                self.next_token()
                result += self.term()  # TODO change to += something
            elif self.token == Tokens.MINUS_TOKEN:
                self.next_token()
                result += self.term()  # TODO change to -= something

        return 'EXPRESSION ' + result

    def term(self):
        result = ''
        result += self.factor()

        while self.token == Tokens.TIMES_TOKEN or self.token == Tokens.DIV_TOKEN:
            if self.token == Tokens.TIMES_TOKEN:
                self.next_token()
                result += self.factor()  # TODO change to *= something
            elif self.token == Tokens.DIV_TOKEN:
                self.next_token()
                result += self.factor()  # TODO change to /= something

        return 'TERM ' + result

    def factor(self):
        result = ''
        if self.token == Tokens.IDENT:
            result += self.designator()
        elif self.token == Tokens.NUMBER:
            result += self.tokenizer.last_number
            self.next_token()
        elif self.token == Tokens.OPEN_PAREN_TOKEN:
            self.next_token()
            result += self.expression()
        elif self.token == Tokens.CALL_TOKEN:
            self.next_token()
            self.func_call()

        return 'FACTOR ' + result

    def relation(self):
        result = ''
        result += self.expression()
        if self.token > 25 or self.token < 20:
            self.tokenizer.error(
                f"SyntaxError: expected relOp got {self.tokenizer.get_token_from_index(self.token)}")
        else:
            result += self.expression()

        return 'RELATION ' + result
