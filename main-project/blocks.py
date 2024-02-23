from enum import Enum

from operations import Operations
from ssa import Instruction


class BlockRelation(Enum):
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
        self.children = {}

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
    def __init__(self, idn=None, join=False, while_block=False):
        super().__init__(idn)
        self.dom = []
        self.join = join
        self.while_block = while_block
        self.instructions = {}
        self.instruction_order_list = []
        self.vars: dict = {}
        self.updated_vars = set()
        self.phi_vars = set()
        self.parents: dict = {}
        self.children: {}
        self.available_phis = []
        self.hidden_first_instr = -1

    def update_id(self, idn):
        self.id = idn

    def update_join(self, join):
        self.join = join

    def is_while(self):
        return self.while_block

    def set_hidden_first_instr(self, instr):
        self.hidden_first_instr = instr

    def get_hidden_first_instr(self):
        return self.hidden_first_instr

    def is_first_hidden_instr(self):
        return self.hidden_first_instr != -1

    def add_new_instr(self, instr_id, op=None, x=None, y=None, start=False):
        inst = Instruction(instr_id, op, x, y)
        self.instructions[instr_id] = inst

        if start:
            self.instruction_order_list.insert(0, inst)
        else:
            self.instruction_order_list.append(inst)

        if op == Operations.PHI:
            self.available_phis.append(inst)
        return instr_id

    def get_instructions(self):
        return self.instructions

    def get_instruction_order_list(self):
        return self.instruction_order_list

    def get_vars(self):
        return self.vars

    def get_updated_vars(self):
        return self.updated_vars

    def add_var_assignment(self, var, instruction_number, update_var=True, while_block=False):
        if not while_block:
            self.vars[var] = instruction_number
        if update_var:
            self.updated_vars.add(var)

    def add_parent(self, parent_block: 'BasicBlock', parent_type: BlockRelation):
        self.parents[parent_block] = parent_type

    def remove_parent(self, parent_block: 'BasicBlock'):
        self.parents.pop(parent_block)

    def get_parents(self):
        return self.parents

    def add_child(self, child_block: 'BasicBlock', child_type: BlockRelation):
        self.children[child_block] = child_type

    def remove_child(self, child_block: 'BasicBlock'):
        self.children.pop(child_block)

    def get_children(self):
        return self.children

    def find_first_instr(self):
        if not self.instructions:
            return None
        return self.instruction_order_list[0].get_id()

    def update_instruction(self, instr_idn, x=None, y=None):
        instr: Instruction = self.instructions[instr_idn]
        if x:
            instr.x = x
        if y:
            instr.y = y

    def get_available_phi_instruction(self):
        return self.available_phis.pop(0)

    def add_phi_var(self, phi_var):
        self.phi_vars.add(phi_var)

    def get_phi_vars(self):
        return self.phi_vars


class Blocks:
    def __init__(self, baseSSA, initial_block):
        self.baseSSA = baseSSA
        self.id_count = 0
        self.constant_block = ConstantBlock(0)
        self.blocks_list: list[BasicBlock] = []
        self.current_block: BasicBlock = initial_block
        self.current_join_block = None
        self.leaf_joins_if = []
        self.leaf_joins_while = []

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

    def update_current_block(self, new_current_block):
        self.current_block = new_current_block

    def add_var_to_current_block(self, var, instruction_number):
        self.current_block.add_var_assignment(var, instruction_number)

    def find_var_idn(self, var):
        # find the instr id for a var
        return self.current_block.get_vars()[var]

    def update_current_join_block(self, block):
        self.current_join_block = block

    def get_current_join_block(self):
        return self.current_join_block

    def get_lowest_leaf_join_block_if(self):
        return self.leaf_joins_if.pop(0)

    def update_leaf_joins_if(self, join_block):
        # Check if a new join is a leaf join block, i.e., whether it is not a child of another join block.
        if self.leaf_joins_if and self.leaf_joins_if[-1] in join_block.get_parents():
            self.leaf_joins_if[-1] = join_block
        else:
            self.leaf_joins_if.append(join_block)

    def get_left_joins_while(self):
        return self.leaf_joins_while

    def get_lowest_leaf_join_block_while(self):
        return self.leaf_joins_while.pop(0)

    def update_leaf_joins_while(self, join_block):
        if self.leaf_joins_while and self.leaf_joins_while[-1] in join_block.get_parents():
            self.leaf_joins_while[-1] = join_block
        else:
            self.leaf_joins_while.append(join_block)
