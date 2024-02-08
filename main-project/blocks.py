from enum import Enum

from ssa import Instruction


class ParentType(Enum):
    NORMAL = 1
    BRANCH = 2
    FALL_THROUGH = 3
    DOM = 4

    def __str__(self):
        if self.value == 3:
            return "fall-through"
        else:
            return self.name.lower()


class Block:
    def __init__(self, id_count=None, parent_block=None, parent_type=None):
        self.id = id_count

    def __str__(self):
        return f"BB{self.id}"

    def get_id(self):
        return self.id

    def update_id(self, id_count):
        self.id = id_count


class ConstantBlock(Block):
    def __init__(self, idn):
        super().__init__(idn)
        self.id = idn
        self.constants = {}

    def add_constant(self, idn, constant):
        self.constants[constant] = idn

    def get_constant_id(self, constant):
        return self.constants[constant]


class BasicBlock(Block):
    def __init__(self, id_count=None, first_parent_block=None, first_parent_type=None):
        super().__init__(id_count, first_parent_block, first_parent_type)
        self.dom = []
        self.join = False
        self.instructions = {}
        self.vars: dict = {}
        self.parents: dict = {first_parent_block: first_parent_type} if first_parent_block else {}

    def add_instruction(self, instruction_id, instruction: Instruction):
        self.instructions[instruction_id] = instruction

    def get_instructions(self):
        return self.instructions

    def get_vars(self):
        return self.vars

    def update_var_assignment(self, var, instruction_number):
        self.vars[var] = instruction_number

    def add_parent(self, parent_block: 'BasicBlock', parent_type: ParentType):
        self.parents[parent_block] = parent_type

    def get_parents(self):
        return self.parents

    def find_first_instr(self):
        return min(self.instructions)

    def update_instruction(self, instr_idn, idn_left=None, idn_right=None):
        instr = self.instructions[instr_idn]
        if idn_left:
            instr.id_left = idn_left
        if idn_right:
            instr.id_right = idn_right


class Blocks:
    def __init__(self, baseSSA, initial_block):
        self.baseSSA = baseSSA
        self.id_count = 0
        self.constant_block = ConstantBlock(0)
        self.blocks_list: list[BasicBlock] = []
        self.current_block: BasicBlock = initial_block

    def get_current_block(self):
        return self.current_block

    def get_constant_block(self):
        return self.constant_block

    def get_blocks_list(self):
        return self.blocks_list

    def add_block(self, block):
        block.update_id(self.get_new_block_id())
        self.blocks_list.append(block)
        self.current_block = block

    def get_new_block_id(self):
        self.id_count += 1
        return self.id_count

    def add_constant(self, constant):
        if constant not in self.constant_block.constants:
            self.constant_block.add_constant(self.baseSSA.get_new_instr_id(), constant)

    def get_constant_id(self, constant):
        return self.constant_block.get_constant_id(constant)

    def add_var_to_current_block(self, var, instruction_number):
        self.current_block.update_var_assignment(var, instruction_number)

    def find_var_idn(self, var):
        # TODO we need to consider join/dominating. Since a var could have two idn in then/else so need the join one
        def find_var_idn_helper(var_inside, cur_block):
            if var_inside in cur_block.get_vars():
                return cur_block.get_vars()[var_inside]

            parents = cur_block.get_parents()
            if parents:
                for p in parents:
                    find_var_idn_helper(var_inside, p)
            else:
                return

        return find_var_idn_helper(var, self.current_block)
