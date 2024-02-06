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
    def __init__(self, id_count=None):
        self.id = id_count

    def __str__(self):
        return f"BB{self.id}"

    def get_id(self):
        return self.id

    def update_id(self, id_count):
        self.id = id_count


class ConstantBlock(Block):
    def __init__(self, id_count):
        super().__init__(id_count)
        self.id = id_count
        self.constants = {}

    def add_constant(self, instruction_id, constant):
        if constant not in self.constants:
            self.constants[constant] = instruction_id


class BasicBlock(Block):
    def __init__(self, id_count=None, parent_block=None, parent_type=None):
        super().__init__(id_count)
        self.dom = []
        self.branch = None
        self.fall_through = None
        self.join = False
        self.instructions = {}
        self.parents: dict = {parent_block: parent_type}

    def add_fall_through(self, then_block):
        self.fall_through = then_block

    def add_branch(self, else_block):
        self.branch = else_block

    def add_parent(self, parent_block: 'BasicBlock', parent_type: ParentType):
        self.parents[parent_block] = parent_type

    def get_parents(self):
        return self.parents

    def add_instruction(self, instruction_id, instruction: Instruction):
        self.instructions[instruction_id] = instruction

    def get_instructions(self):
        return self.instructions


class Blocks:
    def __init__(self):
        self.id_count = 0
        self.constant_block = ConstantBlock(0)
        self.blocks_list: list[BasicBlock] = []
        self.current_block = self.constant_block

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

    def add_constant(self, id_count, constant):
        self.constant_block.add_constant(id_count, constant)
