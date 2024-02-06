from blocks import Blocks, BasicBlock
from ssa import BaseSSA
from tokenizer import Tokenizer
from tokens import Tokens


class Parser:
    def __init__(self, file_name):
        self.tokenizer = Tokenizer(file_name)
        self.token: int = 0
        self.symbolTable = {}
        self.arrayTable = {}
        self.blocks = Blocks()
        self.baseSSA = BaseSSA()
        self.next_token()

    def next_token(self):
        self.token = self.tokenizer.get_next_token()

    def reserved_identifier(self):
        if self.token <= self.tokenizer.max_reserved_id:
            self.tokenizer.error(
                f"SyntaxError: expected ident got {self.tokenizer.get_token_from_index(self.token)}")
            return True
        else:
            return False

    def check_identifier(self):
        reserved = self.reserved_identifier()
        if not reserved:
            if self.token not in self.symbolTable:
                self.tokenizer.error(
                    f"SyntaxError: the {self.tokenizer.last_id} has not been initialized. It is now initialized to 0")
                self.symbolTable[self.token] = 0
                self.next_token()
                return True
            else:
                self.next_token()
                return True
        else:
            return False

    def check_token(self, token_type):
        if self.token != token_type:
            self.tokenizer.error(
                f"SyntaxError: expected {self.tokenizer.get_token_from_index(token_type)} "
                f"got {self.tokenizer.get_token_from_index(self.token)}")
            return False
        else:
            self.next_token()
            return True

    def computation(self):
        result = ''

        if self.check_token(Tokens.MAIN_TOKEN):
            self.next_token()

            # { varDecl } which starts with typeDecl starting with either "var" or "array"
            while self.token > self.tokenizer.max_reserved_id or self.token == Tokens.ARR_TOKEN:
                result += self.var_declaration()

            # { funcDecl } -> [ "void" ] "function"...
            while self.token == Tokens.VOID_TOKEN or self.token == Tokens.FUNC_TOKEN:
                self.next_token()
                if self.token == Tokens.FUNC_TOKEN:
                    self.next_token()
                result += self.func_declaration()

            # "{" statSequence
            if self.token == Tokens.BEGIN_TOKEN:
                self.next_token()
                result += self.stat_sequence()
                self.check_token(Tokens.END_TOKEN)

            # final "."
            self.check_token(Tokens.PERIOD_TOKEN)

        return 'COMPUTATION ' + result

    def var_declaration(self):  # TODO should it return anything/make table with variables as None?
        result = ''
        # Handle arrays
        if self.token == Tokens.OPEN_BRACKET_TOKEN:  # TODO Array stuff
            self.next_token()
            result += self.array_declaration()

        # Check if valid ident
        self.reserved_identifier()
        self.next_token()

        # Check for additional idents seperated by ","
        while self.token == Tokens.COMMA_TOKEN:
            self.next_token()
            self.reserved_identifier()
            self.next_token()

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

        return 'SOMETHING'

    def stat_sequence(self):
        # statement
        result = self.statement()
        # Check for additional statements
        while self.token == Tokens.SEMI_TOKEN:
            self.next_token()
            result = self.statement()

        return 'SOMETHING'

    def statement(self):
        if self.token == Tokens.LET_TOKEN:
            self.next_token()
            result = self.assignment()
        elif self.token == Tokens.FUNC_TOKEN:
            self.next_token()
            result = self.func_call()
        elif self.token == Tokens.IF_TOKEN:
            self.next_token()
            result = self.if_statement()
        elif self.token == Tokens.WHILE_TOKEN:
            self.next_token()
            result = self.while_statement()
        elif self.token == Tokens.RETURN_TOKEN:
            self.next_token()
            result = self.return_statement()

        return 'SOMETHING'

    def assignment(self):
        if not self.reserved_identifier():
            designator = self.token  # TODO ARRAY distinguish
            self.next_token()
            # "<-"
            self.check_token(Tokens.BECOMES_TOKEN)
            expression = self.expression()

            self.symbolTable[designator] = expression

        return 'SOMETHING'

    def func_call(self):
        # Predefined functions
        if self.token == Tokens.INPUT_NUM_TOKEN:
            self.next_token()
            self.check_token(Tokens.OPEN_PAREN_TOKEN)
            self.check_token(Tokens.CLOSE_PAREN_TOKEN)
        elif self.token == Tokens.OUTPUT_NUM_TOKEN:
            self.next_token()
            self.check_token(Tokens.OPEN_PAREN_TOKEN)
            result = self.expression()
            self.check_token(Tokens.CLOSE_PAREN_TOKEN)
        elif self.token == Tokens.OUTPUT_NEW_LINE_TOKEN:
            self.next_token()
            self.check_token(Tokens.OPEN_PAREN_TOKEN)
            self.check_token(Tokens.CLOSE_PAREN_TOKEN)
        else:  # TODO: add later for user defined funcs
            self.check_identifier()

            if self.check_token(Tokens.OPEN_PAREN_TOKEN):
                result = self.expression()
                while self.token == Tokens.COMMA_TOKEN:
                    self.next_token()
                    result = self.expression()
                self.check_token(Tokens.CLOSE_PAREN_TOKEN)

        return 'SOMETHING'

    def if_statement(self):
        # if part
        if_block = BasicBlock(parent=self.blocks.get_current_block())
        self.blocks.add_block(if_block)
        left_side, rel_op, right_side = self.relation()

        # then part
        self.check_token(Tokens.THEN_TOKEN)
        then_block = BasicBlock(parent=if_block)
        self.blocks.add_block(then_block)
        if_block.add_fall_through(then_block)
        stat_sequence_then = self.stat_sequence()

        # else part
        if self.token == Tokens.ELSE_TOKEN:
            self.next_token()
            else_block = BasicBlock(parent=if_block)
            self.blocks.add_block(else_block)
            if_block.add_branch(else_block)
            stat_sequence_else = self.stat_sequence()

        self.check_token(Tokens.FI_TOKEN)
        return 'SOMETHING'

    def while_statement(self):
        left_side, rel_op, right_side = self.relation()
        self.check_token(Tokens.DO_TOKEN)
        stat_sequence = self.stat_sequence()
        self.check_token(Tokens.OD_TOKEN)
        return 'SOMETHING'

    def return_statement(self):
        return self.expression()

    def designator(self):
        designator = self.token
        if self.check_identifier():
            while self.token == Tokens.OPEN_BRACKET_TOKEN:  # TODO fix for arrays later
                self.next_token()
                designator += self.expression()
                self.check_token(Tokens.CLOSE_BRACKET_TOKEN)
            return designator
        else:
            return 0  # TODO what to return in this case - like do we stop or continue?

    def expression(self):  # TODO else clause should return nothing FOR sel.return [] can be blank
        result = self.term()

        while self.token == Tokens.PLUS_TOKEN or self.token == Tokens.MINUS_TOKEN:
            if self.token == Tokens.PLUS_TOKEN:
                self.next_token()
                result += self.term()
            elif self.token == Tokens.MINUS_TOKEN:
                self.next_token()
                result -= self.term()

        return result

    def term(self):
        result = self.factor()

        while self.token == Tokens.TIMES_TOKEN or self.token == Tokens.DIV_TOKEN:
            if self.token == Tokens.TIMES_TOKEN:
                self.next_token()
                result *= self.factor()
            elif self.token == Tokens.DIV_TOKEN:
                self.next_token()
                result /= self.factor()

        return result

    def factor(self):  # returns the number from either designator, number, ( expression ), or funcCall
        if self.token > self.tokenizer.max_reserved_id:
            result = self.designator()
        elif self.token == Tokens.NUMBER:
            result = self.tokenizer.last_number
            self.blocks.add_constant(self.baseSSA.get_new_instr_id(), result)
            self.next_token()
        elif self.token == Tokens.OPEN_PAREN_TOKEN:
            self.next_token()
            result = self.expression()
            self.check_token(Tokens.CLOSE_PAREN_TOKEN)
            self.next_token()
        elif self.token == Tokens.CALL_TOKEN:
            self.next_token()
            result = self.func_call()
        else:
            return ''

        return result

    def relation(self):
        left_side = self.expression()
        if self.token > 25 or self.token < 20:
            self.tokenizer.error(
                f"SyntaxError: expected relOp got {self.tokenizer.get_token_from_index(self.token)}")
            return False  # TODO what to return in this case???
        else:
            rel_op = self.token
            self.next_token()
            right_side = self.expression()
            return left_side, rel_op, right_side
