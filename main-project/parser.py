from blocks import Blocks, BasicBlock, ParentType
from operations import Operations
from ssa import BaseSSA
from tokenizer import Tokenizer
from tokens import Tokens


class Parser:
    def __init__(self, file_name):
        self.tokenizer = Tokenizer(file_name)
        self.token: int = 0
        self.symbolTable = {}  # id token -> var name
        self.arrayTable = {}
        self.baseSSA = BaseSSA()
        self.blocks = Blocks(self.baseSSA, None)
        self.setup_blocks()
        self.next_token()

    def setup_blocks(self):
        initial_block = BasicBlock(first_parent_block=self.blocks.get_constant_block(),
                                   first_parent_type=ParentType.NORMAL)
        self.blocks.add_block(initial_block)

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
                self.symbolTable[self.token] = self.tokenizer.last_id
                self.blocks.add_constant(0)
                self.blocks.add_var_to_current_block(self.token, self.blocks.get_constant_id(0))
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
        if self.check_token(Tokens.MAIN_TOKEN):
            self.next_token()

            # { varDecl } which starts with typeDecl starting with either "var" or "array"
            while self.token > self.tokenizer.max_reserved_id or self.token == Tokens.ARR_TOKEN:
                self.var_declaration()

            # { funcDecl } -> [ "void" ] "function"...
            while self.token == Tokens.VOID_TOKEN or self.token == Tokens.FUNC_TOKEN:
                self.next_token()
                if self.token == Tokens.FUNC_TOKEN:
                    self.next_token()
                self.func_declaration()

            # "{" statSequence
            if self.token == Tokens.BEGIN_TOKEN:
                self.next_token()
                self.stat_sequence()
                self.check_token(Tokens.END_TOKEN)

            # final "."
            self.check_token(Tokens.PERIOD_TOKEN)

        return

    def var_declaration(self):
        # Handle arrays
        if self.token == Tokens.OPEN_BRACKET_TOKEN:  # TODO Array stuff
            self.next_token()
            self.array_declaration()

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

        return

    def array_declaration(self):
        # "["
        while self.check_token(Tokens.OPEN_BRACKET_TOKEN):
            # number
            self.check_token(Tokens.NUMBER)
            # "]"
            self.check_token(Tokens.CLOSE_BRACKET_TOKEN)

        return

    def func_declaration(self):
        # Check if valid ident
        self.check_identifier()
        # formalParam
        self.formal_parameter()
        # Check for ";"
        self.check_token(Tokens.SEMI_TOKEN)
        # funcBody
        self.func_body()
        # Check for ";"
        self.check_token(Tokens.SEMI_TOKEN)

        return

    def formal_parameter(self):
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
        return

    def func_body(self):
        # { varDecl } which starts with typeDecl starting with either "var" or "array"
        while self.token == Tokens.VAR_TOKEN or self.token == Tokens.ARR_TOKEN:
            self.next_token()
            self.var_declaration()

        # Check for "{"
        self.check_token(Tokens.BEGIN_TOKEN)
        # Check for optional statSequence
        self.stat_sequence()
        # Check for "}"
        self.check_token(Tokens.END_TOKEN)

        return

    def stat_sequence(self):
        # statement
        self.statement()
        # Check for additional statements
        while self.token == Tokens.SEMI_TOKEN:
            self.next_token()
            self.statement()

        return

    def statement(self):
        if self.token == Tokens.LET_TOKEN:
            self.next_token()
            self.assignment()
        elif self.token == Tokens.FUNC_TOKEN:
            self.next_token()
            self.func_call()
        elif self.token == Tokens.IF_TOKEN:
            self.next_token()
            self.if_statement()
        elif self.token == Tokens.WHILE_TOKEN:
            self.next_token()
            self.while_statement()
        elif self.token == Tokens.RETURN_TOKEN:
            self.next_token()
            self.return_statement()

        return

    def assignment(self):
        if not self.reserved_identifier():
            designator = self.token  # TODO ARRAY distinguish
            self.symbolTable[designator] = self.tokenizer.last_id
            self.next_token()
            # "<-"
            self.check_token(Tokens.BECOMES_TOKEN)
            idn = self.expression()

            self.blocks.add_var_to_current_block(designator, idn)

        return

    def func_call(self):
        result = ''
        # Predefined functions
        if self.token == Tokens.INPUT_NUM_TOKEN:  # InputNum()
            self.next_token()
            self.check_token(Tokens.OPEN_PAREN_TOKEN)
            self.check_token(Tokens.CLOSE_PAREN_TOKEN)
            self.blocks.get_current_block().add_new_instr(self.baseSSA.get_new_instr_id(), Operations.READ)
        elif self.token == Tokens.OUTPUT_NUM_TOKEN:  # OutputNum(x)
            self.next_token()
            self.check_token(Tokens.OPEN_PAREN_TOKEN)
            x = self.expression()
            self.check_token(Tokens.CLOSE_PAREN_TOKEN)
            self.blocks.get_current_block().add_new_instr(self.baseSSA.get_new_instr_id(), Operations.WRITE, x)
        elif self.token == Tokens.OUTPUT_NEW_LINE_TOKEN:  # OutputNewLine()
            self.next_token()
            self.check_token(Tokens.OPEN_PAREN_TOKEN)
            self.check_token(Tokens.CLOSE_PAREN_TOKEN)
            self.blocks.get_current_block().add_new_instr(self.baseSSA.get_new_instr_id(), Operations.WRITE_NL)
        else:  # TODO: user funcs
            self.check_identifier()
            if self.check_token(Tokens.OPEN_PAREN_TOKEN):
                result = self.expression()
                while self.token == Tokens.COMMA_TOKEN:
                    self.next_token()
                    result = self.expression()
                self.check_token(Tokens.CLOSE_PAREN_TOKEN)

        return result

    def if_statement(self):
        # if part
        left_side, rel_op_instr, right_side = self.relation()
        if_block = self.blocks.get_current_block()
        # make comparison instr
        cmp_instr_idn = if_block.add_new_instr(self.baseSSA.get_new_instr_id(), Operations.CMP, left_side, right_side)
        # add the branch instr (branch instr added when known below)
        branch_instr_idn = if_block.add_new_instr(self.baseSSA.get_new_instr_id(), op=rel_op_instr,
                                                  idn_left=cmp_instr_idn)

        # then part
        self.check_token(Tokens.THEN_TOKEN)
        then_block = BasicBlock(first_parent_block=if_block, first_parent_type=ParentType.FALL_THROUGH)
        self.blocks.add_block(then_block)
        if_block.add_fall_through(then_block)
        self.stat_sequence()

        # else part (might be empty)
        else_block = BasicBlock(first_parent_block=if_block, first_parent_type=ParentType.BRANCH)
        self.blocks.add_block(else_block)
        if_block.add_branch(else_block)
        if self.token == Tokens.ELSE_TOKEN:
            self.next_token()
            self.stat_sequence()
        else:  # empty else block
            else_block.add_new_instr(self.baseSSA.get_new_instr_id())

        self.check_token(Tokens.FI_TOKEN)
        if_block.update_instruction(branch_instr_idn, idn_right=else_block.find_first_instr())

        return

    def while_statement(self):
        left_side, rel_op, right_side = self.relation()
        self.blocks.get_current_block().add_new_instr(self.baseSSA.get_new_instr_id(), Operations.CMP, left_side,
                                                      right_side)

        self.check_token(Tokens.DO_TOKEN)
        current_block = self.blocks.get_current_block()

        then_block = BasicBlock(first_parent_block=self.blocks.get_current_block(),
                                first_parent_type=ParentType.FALL_THROUGH)
        self.blocks.add_block(then_block)
        current_block.add_fall_through(then_block)

        self.stat_sequence()
        self.check_token(Tokens.OD_TOKEN)

        else_block = BasicBlock(first_parent_block=self.blocks.get_current_block(), first_parent_type=ParentType.BRANCH)
        self.blocks.add_block(else_block)
        current_block.add_branch(else_block)

        return

    def return_statement(self):  # TODO user func ?
        return self.expression()

    def designator(self):
        designator = self.token

        if self.check_identifier():
            if self.token == Tokens.OPEN_BRACKET_TOKEN:  # array
                while self.token == Tokens.OPEN_BRACKET_TOKEN:  # TODO fix for arrays later
                    self.next_token()
                    designator += self.expression()
                    self.check_token(Tokens.CLOSE_BRACKET_TOKEN)
                    return 0, "something", True
            else:  # normal id
                return designator, False
        else:
            return

    def expression(self):  # TODO else clause should return nothing FOR sel.return [] can be blank
        idn_left = self.term()

        while self.token == Tokens.PLUS_TOKEN or self.token == Tokens.MINUS_TOKEN:
            if self.token == Tokens.PLUS_TOKEN:
                self.next_token()
                idn_right = self.factor()
                # = idn_left so that if we e.g. have 2 + 2 + 2 then the id for the first 2 * 2 becomes the next left
                idn_left = self.blocks.get_current_block()(self.baseSSA.get_new_instr_id(), Operations.ADD, idn_left,
                                                           idn_right)
            elif self.token == Tokens.MINUS_TOKEN:
                self.next_token()
                idn_right = self.factor()
                idn_left = self.blocks.get_current_block()(self.baseSSA.get_new_instr_id(), Operations.SUB, idn_left,
                                                           idn_right)

        return idn_left

    def term(self):
        idn_left = self.factor()

        while self.token == Tokens.TIMES_TOKEN or self.token == Tokens.DIV_TOKEN:
            if self.token == Tokens.TIMES_TOKEN:
                self.next_token()
                idn_right = self.factor()
                idn_left = self.blocks.get_current_block()(self.baseSSA.get_new_instr_id(), Operations.MUL, idn_left,
                                                           idn_right)
            elif self.token == Tokens.DIV_TOKEN:
                self.next_token()
                idn_right = self.factor()
                idn_left = self.blocks.get_current_block()(self.baseSSA.get_new_instr_id(), Operations.DIV, idn_left,
                                                           idn_right)

        return idn_left

    def factor(self):  # returns the number from either designator, number, ( expression ), or funcCall
        if self.token > self.tokenizer.max_reserved_id:
            designator, designator_var_name, array = self.designator()
            if array:
                pass  # TODO Handle when array
            else:
                return self.blocks.find_var_idn(designator)
        elif self.token == Tokens.NUMBER:
            num = self.tokenizer.last_number
            self.blocks.add_constant(num)
            constant_id = self.blocks.get_constant_id(num)
            self.next_token()
            return constant_id  # return the id for the constant when it is directly a number
        elif self.token == Tokens.OPEN_PAREN_TOKEN:
            self.next_token()
            result = self.expression()
            self.check_token(Tokens.CLOSE_PAREN_TOKEN)
            self.next_token()
            return result  # return whatever the expression gives (ends up in factor as well)
        elif self.token == Tokens.CALL_TOKEN:
            self.next_token()
            result = self.func_call()
            return result  # return what func call gives
        else:
            return ''  # TODO handle this case

    def relation(self):
        left_side = self.expression()
        if self.token > 25 or self.token < 20:
            self.tokenizer.error(
                f"SyntaxError: expected relOp got {self.tokenizer.get_token_from_index(self.token)}")
            return False  # TODO return what?
        else:
            rel_op = self.token
            rel_op_instr = self.baseSSA.rel_op_to_instr(rel_op)
            self.next_token()
            right_side = self.expression()
            return left_side, rel_op_instr, right_side
