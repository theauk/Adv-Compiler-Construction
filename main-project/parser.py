from blocks import Blocks, BasicBlock, BlockRelation
from operations import Operations
from ssa import BaseSSA
from tokenizer import Tokenizer
from tokens import Tokens
from utils import Utils


class Parser:
    def __init__(self, file_name):
        self.tokenizer = Tokenizer(file_name)
        self.token: int = 0
        self.symbolTable = {}  # id token -> var name
        self.arrayTable = {}  # designator -> (length of dim 1, length of dim 2...)
        self.baseSSA = BaseSSA()
        self.blocks = Blocks(self.baseSSA, None)
        self.setup_blocks()
        self.utils = Utils(self.blocks, self.baseSSA)
        self.next_token()
        self.while_stack = []
        self.outer_while_blocks = []
        self.if_branch_blocks = []

    def in_while(self):
        return len(self.while_stack) > 0

    def setup_blocks(self):
        initial_block = BasicBlock()
        initial_block.add_parent(parent_block=self.blocks.get_constant_block(), parent_type=BlockRelation.NORMAL)
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
            if self.token not in self.blocks.get_current_block().get_vars() or \
                    self.blocks.get_current_block().get_vars()[self.token] is None:
                if self.token not in self.arrayTable:
                    self.tokenizer.error(
                        f"SyntaxError: {self.tokenizer.last_id} has not been initialized. It is now initialized to 0")
                    self.symbolTable[self.token] = self.tokenizer.last_id
                    self.blocks.add_constant(0)
                    self.blocks.add_var_to_current_block(self.token, self.blocks.get_constant_instr(0))

                else:
                    if self.blocks.get_current_block().get_array_assignment()[self.token] is None:
                        self.tokenizer.error(
                            f"SyntaxError: {self.tokenizer.last_id} has not been initialized.")
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
            self.next_token()
            return False
        else:
            self.next_token()
            return True

    def computation(self):
        if self.check_token(Tokens.MAIN_TOKEN):

            # { varDecl } which starts with typeDecl starting with either "var" or "array"
            while self.token == Tokens.VAR_TOKEN or self.token == Tokens.ARR_TOKEN:
                self.var_declaration()
                self.check_token(Tokens.SEMI_TOKEN)

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

            # Add end instruction
            instr_id = self.baseSSA.get_new_instr_id()
            self.blocks.add_new_instr(self.in_while(), block=self.blocks.get_current_block(), instr_id=instr_id,
                                      op=Operations.END)

            if len(self.outer_while_blocks) > 0:
                self.utils.fix_branching(self.outer_while_blocks, False)

            if len(self.if_branch_blocks) > 0:
                self.utils.fix_branching(self.if_branch_blocks, True)

            self.utils.fix_id_numbering()

        return

    def var_declaration(self):
        # Handle arrays
        if self.token == Tokens.ARR_TOKEN:
            self.array_declaration()
        else:
            self.next_token()
            # Handle non-array parameters
            # Check if valid ident
            if not self.reserved_identifier():
                self.blocks.get_current_block().add_var_assignment(self.token, None)
                self.symbolTable[self.token] = self.tokenizer.last_id
            self.next_token()

        # Check for additional idents seperated by ","
        if self.token == Tokens.COMMA_TOKEN:
            self.var_declaration()

        return

    def array_declaration(self):
        lengths_of_dimensions = []
        self.next_token()
        self.check_token(Tokens.OPEN_BRACKET_TOKEN)
        self.check_token(Tokens.NUMBER)
        lengths_of_dimensions.append(self.tokenizer.last_number)
        self.check_token(Tokens.CLOSE_BRACKET_TOKEN)

        while self.token == Tokens.OPEN_BRACKET_TOKEN:
            self.next_token()
            self.check_token(Tokens.NUMBER)
            lengths_of_dimensions.append(self.tokenizer.last_number)
            self.check_token(Tokens.CLOSE_BRACKET_TOKEN)

        # Check if valid ident
        if not self.reserved_identifier():
            self.blocks.get_current_block().add_var_assignment(self.token, None)
            self.symbolTable[self.token] = self.tokenizer.last_id

        self.symbolTable[self.token] = self.tokenizer.last_id
        self.arrayTable[self.token] = tuple(lengths_of_dimensions)
        self.blocks.get_current_block().add_array(self.token, lengths_of_dimensions)

        self.next_token()

    def func_declaration(self):
        self.check_identifier()
        self.formal_parameter()
        self.check_token(Tokens.SEMI_TOKEN)
        self.func_body()
        self.check_token(Tokens.SEMI_TOKEN)

        return

    def formal_parameter(self):
        self.check_token(Tokens.OPEN_PAREN_TOKEN)
        # Check for optional ident
        if self.token == Tokens.IDENT:
            self.check_identifier()
            # Check for additional parameters
            while self.token == Tokens.COMMA_TOKEN:
                self.next_token()
                self.check_identifier()
        self.check_token(Tokens.CLOSE_PAREN_TOKEN)

        return

    def func_body(self):
        # { varDecl } which starts with typeDecl starting with either "var" or "array"
        while self.token == Tokens.VAR_TOKEN or self.token == Tokens.ARR_TOKEN:
            self.next_token()
            self.var_declaration()

        self.check_token(Tokens.BEGIN_TOKEN)
        self.stat_sequence()
        self.check_token(Tokens.END_TOKEN)

        return

    def stat_sequence(self):
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
        elif self.token == Tokens.CALL_TOKEN:
            self.next_token()
            self.func_call()
        elif self.token == Tokens.IF_TOKEN:
            self.next_token()
            self.if_statement()
            self.blocks.update_leaf_joins(self.blocks.current_block)
        elif self.token == Tokens.WHILE_TOKEN:
            self.next_token()
            self.while_statement()
            self.blocks.update_leaf_joins(self.blocks.current_block)
        elif self.token == Tokens.RETURN_TOKEN:
            self.next_token()
            self.return_statement()

        return

    def assignment(self):
        if not self.reserved_identifier():
            designator, is_array, indices = self.designator(lhs=True)
            # "<-"
            self.check_token(Tokens.BECOMES_TOKEN)
            idn, idn_var = self.expression()

            if not is_array:
                self.blocks.add_var_to_current_block(designator, idn)

                # Check if phi should be added (given we have a current join block and have not already made a phi ready
                # for a certain variable)
                current_join_block = self.blocks.get_current_join_block()
                if current_join_block and designator not in current_join_block.get_phi_vars():
                    self.utils.create_phi_instruction(self.in_while(), current_join_block, designator)
            else:
                self.blocks.get_current_block().store_element_in_array(self.baseSSA.get_new_instr_id(), designator, idn,
                                                                       indices)

        return

    def return_statement(self):
        self.blocks.get_current_block().set_as_return_block()
        x, x_var = self.expression()
        self.blocks.add_new_instr(self.in_while(), self.blocks.get_current_block(), self.baseSSA.get_new_instr_id(),
                                  Operations.RET, x=x, x_var=x_var)
        return

    def designator(self, lhs=False):
        designator = self.token

        if not lhs:
            self.check_identifier()
        else:
            self.next_token()

        indices = []
        if self.token == Tokens.OPEN_BRACKET_TOKEN:  # array
            while self.token == Tokens.OPEN_BRACKET_TOKEN:
                self.check_token(Tokens.OPEN_BRACKET_TOKEN)
                exp = self.expression()
                indices.append(exp[0])
                self.check_token(Tokens.CLOSE_BRACKET_TOKEN)

            array = self.blocks.get_current_block().get_array(designator)

            if not lhs:
                instr = self.baseSSA.get_new_instr_id()
                self.blocks.add_new_instr(self.in_while(), self.blocks.get_current_block(), instr, Operations.LOAD)

                result = array
                for index in indices:
                    result = result[index]

                if not result:
                    self.tokenizer.error(
                        f"array index has not been initialized for array {self.symbolTable[designator]}")

                return result, True, indices  # TODO fix since it does not do designator like the others
                # TODO: this will be a load instruction somewhere and you have to check for "cse" loads
                # it will probably be fine to return the result that is there as long as you also do the load etc.

            # TODO: you have to check if you need to kill
            return designator, True, indices
        else:  # normal id
            return designator, False, indices

    def expression(self):
        idn_left, idn_left_var = self.term()

        while self.token == Tokens.PLUS_TOKEN or self.token == Tokens.MINUS_TOKEN:
            if self.token == Tokens.PLUS_TOKEN:
                self.next_token()
                idn_right, idn_right_var = self.term()
                # = idn_left so that if we e.g. have 2 + 2 + 2 then the id for the first 2 * 2 becomes the next left
                idn_left = self.blocks.add_new_instr(self.in_while(), self.blocks.get_current_block(),
                                                     self.baseSSA.get_new_instr_id(), Operations.ADD, idn_left,
                                                     idn_right, x_var=idn_left_var, y_var=idn_right_var)
                idn_left_var = None  # TODO check that it is not a problem that idn_left_var is not updated
            elif self.token == Tokens.MINUS_TOKEN:
                self.next_token()
                idn_right, idn_right_var = self.term()
                idn_left = self.blocks.add_new_instr(self.in_while(), self.blocks.get_current_block(),
                                                     self.baseSSA.get_new_instr_id(), Operations.SUB, idn_left,
                                                     idn_right, x_var=idn_left_var, y_var=idn_right_var)
                idn_left_var = None  # TODO check that it is not a problem that idn_left_var is not updated

        return idn_left, idn_left_var

    def term(self):
        idn_left, idn_left_var = self.factor()

        while self.token == Tokens.TIMES_TOKEN or self.token == Tokens.DIV_TOKEN:
            if self.token == Tokens.TIMES_TOKEN:
                self.next_token()
                idn_right, idn_right_var = self.factor()
                idn_left = self.blocks.add_new_instr(self.in_while(), self.blocks.get_current_block(),
                                                     self.baseSSA.get_new_instr_id(), Operations.MUL, idn_left,
                                                     idn_right, x_var=idn_left_var, y_var=idn_right_var)
                idn_left_var = None  # TODO check that it is not a problem that idn_left_var is not updated
            elif self.token == Tokens.DIV_TOKEN:
                self.next_token()
                idn_right, idn_right_var = self.factor()
                idn_left = self.blocks.add_new_instr(self.in_while(), self.blocks.get_current_block(),
                                                     self.baseSSA.get_new_instr_id(), Operations.DIV, idn_left,
                                                     idn_right, x_var=idn_left_var, y_var=idn_right_var)
                idn_left_var = None  # TODO check that it is not a problem that idn_left_var is not updated

        return idn_left, idn_left_var

    def factor(self):  # returns the number from either designator, number, ( expression ), or funcCall
        if self.token > self.tokenizer.max_reserved_id:
            designator, array, indices = self.designator()
            if array:
                return -1, designator  # TODO: UPDATE for arrays
            else:
                return self.blocks.find_var_given_id(designator), designator
        elif self.token == Tokens.NUMBER:
            num = self.tokenizer.last_number
            self.blocks.add_constant(num)
            constant_instr = self.blocks.get_constant_instr(num)
            self.next_token()
            return constant_instr, None  # return the instr for the constant when it is directly a number
        elif self.token == Tokens.OPEN_PAREN_TOKEN:
            self.next_token()
            result, result_var = self.expression()
            self.check_token(Tokens.CLOSE_PAREN_TOKEN)
            return result, result_var  # return whatever the expression gives (ends up in factor as well)
        elif self.token == Tokens.CALL_TOKEN:
            self.next_token()
            result, result_var = self.func_call()
            return result, result_var  # return what func call gives
        elif self.blocks.get_current_block().is_return_block():
            return None, None
        else:
            self.tokenizer.error(
                f"SyntaxError: expected either {self.tokenizer.get_token_from_index(Tokens.IDENT), self.tokenizer.get_token_from_index(Tokens.NUMBER), self.tokenizer.get_token_from_index(Tokens.OPEN_PAREN_TOKEN), self.tokenizer.get_token_from_index(Tokens.CALL_TOKEN)} "
                f"got {self.tokenizer.get_token_from_index(self.token)}")
            self.next_token()
            return None, None

    def relation(self):
        left_side, left_side_var = self.expression()
        if self.token > 25 or self.token < 20:
            self.tokenizer.error(
                f"SyntaxError: expected relOp got {self.tokenizer.get_token_from_index(self.token)}")
            return
        else:
            rel_op = self.token
            rel_op_instr = self.baseSSA.rel_op_to_instruction(rel_op)
            self.next_token()
            right_side, right_side_var = self.expression()
            return left_side, rel_op_instr, right_side, left_side_var, right_side_var

    def func_call(self):
        # Predefined functions
        if self.token == Tokens.INPUT_NUM_TOKEN:  # InputNum()
            self.next_token()
            if self.token == Tokens.OPEN_PAREN_TOKEN:
                self.check_token(Tokens.OPEN_PAREN_TOKEN)
                self.check_token(Tokens.CLOSE_PAREN_TOKEN)
            idn = self.baseSSA.get_new_instr_id()
            instr = self.blocks.add_new_instr(self.in_while(), self.blocks.get_current_block(), idn, Operations.READ)
            return instr, None
        elif self.token == Tokens.OUTPUT_NUM_TOKEN:  # OutputNum(x)
            self.next_token()
            self.check_token(Tokens.OPEN_PAREN_TOKEN)
            x, x_var = self.expression()
            self.check_token(Tokens.CLOSE_PAREN_TOKEN)
            self.blocks.add_new_instr(self.in_while(), self.blocks.get_current_block(), self.baseSSA.get_new_instr_id(),
                                      Operations.WRITE, x, x_var=x_var)
        elif self.token == Tokens.OUTPUT_NEW_LINE_TOKEN:  # OutputNewLine()
            self.next_token()
            if self.token == Tokens.OPEN_PAREN_TOKEN:
                self.check_token(Tokens.OPEN_PAREN_TOKEN)
                self.check_token(Tokens.CLOSE_PAREN_TOKEN)
            self.blocks.add_new_instr(self.in_while(), self.blocks.get_current_block(), self.baseSSA.get_new_instr_id(),
                                      Operations.WRITE_NL)
        else:  # user funcs
            self.check_identifier()
            if self.check_token(Tokens.OPEN_PAREN_TOKEN):
                self.expression()
                while self.token == Tokens.COMMA_TOKEN:
                    self.next_token()
                    self.expression()
                self.check_token(Tokens.CLOSE_PAREN_TOKEN)

        return None, None

    def if_statement(self):
        # new block below (potentially a join block) but do not add it yet (so that it does not get an ID yet)
        join_block = BasicBlock()
        self.blocks.update_current_join_block(join_block)

        # if part
        left_side, rel_op_instr, right_side, left_side_var, right_side_var = self.relation()
        if_block = self.blocks.get_current_block()
        branch_instr_idn = self.utils.make_relation(if_block, left_side, right_side, rel_op_instr, left_side_var,
                                                    right_side_var, self.in_while())

        join_block.add_dom_parent(if_block)

        # then part
        self.check_token(Tokens.THEN_TOKEN)
        then_block = BasicBlock()
        self.utils.add_relationship(parent_block=if_block, child_block=then_block,
                                    relationship=BlockRelation.FALL_THROUGH)
        self.blocks.add_block(then_block)
        then_block.add_dom_parent(if_block)
        self.stat_sequence()

        # else part (might be empty)
        else_block = BasicBlock()
        self.utils.add_relationship(parent_block=if_block, child_block=else_block, relationship=BlockRelation.BRANCH)
        self.blocks.add_block(else_block)
        else_block.add_dom_parent(if_block)

        # The join block might have changed if there was a nested join inside then so set it back to original
        self.blocks.update_current_join_block(join_block)

        if self.token == Tokens.ELSE_TOKEN:
            self.next_token()
            self.stat_sequence()
        if not else_block.get_instructions():  # empty else block
            self.blocks.add_new_instr(self.in_while(), else_block, self.baseSSA.get_new_instr_id())

        self.check_token(Tokens.FI_TOKEN)
        # update the "branch" instruction/arrow for if so that it points to the first instruction in else
        if_block.update_instruction(branch_instr_idn, y=else_block.find_first_instr())

        # The join block might have changed if there was a nested join inside else so set it back to original
        self.blocks.update_current_join_block(join_block)

        # Add the join block so that it gets an ID
        self.blocks.add_block(join_block)

        # Update parents and children
        if not then_block.get_children() and not else_block.get_children():
            # Case 1: no additional conditional in either then or else
            branch_block = then_block
            self.utils.add_relationship(parent_block=then_block, child_block=join_block,
                                        relationship=BlockRelation.BRANCH)
            self.utils.add_relationship(parent_block=else_block, child_block=join_block,
                                        relationship=BlockRelation.FALL_THROUGH)
        elif not then_block.get_children():
            # Case 2: no additional conditional in then
            fall_through_block = self.blocks.get_lowest_placed_leaf_join_block()
            self.utils.add_relationship(parent_block=fall_through_block, child_block=join_block,
                                        relationship=BlockRelation.FALL_THROUGH)
            self.utils.add_relationship(parent_block=then_block, child_block=join_block,
                                        relationship=BlockRelation.BRANCH)
            else_block = fall_through_block
            branch_block = then_block
        elif not else_block.get_children():
            # Case 3: no additional conditional in else
            branch_block = self.blocks.get_lowest_placed_leaf_join_block()
            self.utils.add_relationship(parent_block=branch_block, child_block=join_block,
                                        relationship=BlockRelation.BRANCH)
            self.utils.add_relationship(parent_block=else_block, child_block=join_block,
                                        relationship=BlockRelation.FALL_THROUGH)
            then_block = branch_block
        else:
            # Case 4: new conditional in both then and else
            then_block = self.blocks.get_lowest_placed_leaf_join_block()
            else_block = self.blocks.get_lowest_placed_leaf_join_block()
            branch_block = else_block
            self.utils.add_relationship(parent_block=then_block, child_block=join_block,
                                        relationship=BlockRelation.FALL_THROUGH)
            self.utils.add_relationship(parent_block=else_block, child_block=join_block,
                                        relationship=BlockRelation.BRANCH)

        if not join_block.get_instructions():  # empty join block
            self.blocks.add_new_instr(self.in_while(), then_block, self.baseSSA.get_new_instr_id())

        if then_block.is_return_block() and else_block.is_return_block():
            join_block.reset_instructions()
            # Remove unused phis due to return statement
            self.utils.remove_unused_phis(join_block)
            self.if_branch_blocks.append(join_block)
            self.blocks.add_new_instr(self.in_while(), block=join_block, instr_id=self.baseSSA.get_new_instr_id(),
                                      op=Operations.BRA)
            join_block.set_as_return_block()
        else:
            self.if_branch_blocks.append(branch_block)
            self.blocks.add_new_instr(self.in_while(), block=branch_block, instr_id=self.baseSSA.get_new_instr_id(),
                                      op=Operations.BRA)
            self.utils.add_phis_if(self.in_while(), if_block, then_block, else_block)

        self.blocks.update_current_join_block(None)

        return

    def while_statement(self):
        self.while_stack.append("while")
        initial_current_block = self.blocks.get_current_block()

        # Check if there is already a block available to be used for a while block. Otherwise, make a new one.
        if len(self.blocks.get_current_block().get_instructions()) == 0:
            while_block = self.blocks.get_current_block()
            while_block.set_while(True)
        else:
            while_block = BasicBlock(while_block=True)
            self.utils.add_relationship(parent_block=self.blocks.get_current_block(), child_block=while_block,
                                        relationship=BlockRelation.NORMAL)
            self.blocks.add_block(while_block)
            while_block.add_dom_parent(initial_current_block, self.in_while())
            self.blocks.update_current_join_block(while_block)

        # Make the cmp and branch instruction
        left_side, rel_op_instr, right_side, left_side_var, right_side_var = self.relation()
        self.utils.make_relation(while_block, left_side, right_side, rel_op_instr, left_side_var, right_side_var,
                                 self.in_while())

        self.check_token(Tokens.DO_TOKEN)

        # Make new then block
        then_block = BasicBlock()
        self.utils.add_relationship(parent_block=while_block, child_block=then_block,
                                    relationship=BlockRelation.FALL_THROUGH)
        self.blocks.add_block(then_block)
        then_block.add_dom_parent(while_block, self.in_while())

        self.stat_sequence()

        self.check_token(Tokens.OD_TOKEN)

        # Handle dangling blocks and potential instructions below od
        if len(self.blocks.get_leaf_joins()) > 0:
            leaf_block: BasicBlock = self.blocks.get_lowest_placed_leaf_join_block()
            leaf_block_parent: BasicBlock = list(leaf_block.get_parents().keys())[0]
            # There are no instructions below od but the block is inside another while.
            # Remove the branch block (since it is not needed) and branch to the while above.
            if len(leaf_block.get_instructions()) == 0 and self.blocks.get_current_join_block() != leaf_block:
                self.blocks.remove_latest_block()
                self.utils.add_relationship(parent_block=leaf_block_parent, child_block=while_block,
                                            relationship=BlockRelation.BRANCH, copy_vars=False)
            elif len(leaf_block.get_children()) == 0:
                # There are instructions below od. Add a branch from that block to top of the current while. Branch
                # value will be updated later
                self.blocks.add_new_instr(self.in_while(), block=leaf_block, instr_id=self.baseSSA.get_new_instr_id(),
                                          op=Operations.BRA)
                self.utils.add_relationship(parent_block=leaf_block, child_block=while_block,
                                            relationship=BlockRelation.BRANCH, copy_vars=False)

        self.utils.add_phis_while(self.in_while(), while_block, then_block)

        # Check if bra instruction should be inserted to create path out of current block if necessary
        if len(self.blocks.get_current_block().get_children()) == 0:
            bra_instr = self.baseSSA.get_new_instr_id()
            self.blocks.add_new_instr(self.in_while(), self.blocks.get_current_block(), bra_instr,Operations.BRA)
            self.utils.add_relationship(parent_block=self.blocks.get_current_block(), child_block=while_block,
                                        relationship=BlockRelation.BRANCH, copy_vars=False)

        if BlockRelation.BRANCH not in while_block.get_children().values():
            # Handle the branch block
            branch_block = BasicBlock()
            self.utils.copy_vars(parent_block=while_block, child_block=branch_block)
            self.blocks.add_block(branch_block)
            self.utils.add_relationship(parent_block=while_block, child_block=branch_block,
                                        relationship=BlockRelation.BRANCH)
            branch_block.add_dom_parent(while_block, self.in_while())

        self.blocks.update_current_join_block(None)
        self.while_stack.pop()

        # Do more passes on most outer while block to update phis, branching and cse if we are no longer in the while
        if not self.in_while():
            self.utils.update_while(while_block)
            self.outer_while_blocks.append(while_block)

        return
