import copy
from enum import Enum

from operations import Operations
from ssa import Instruction


class BlockRelation(Enum):
    NORMAL = 1
    BRANCH = 2
    FALL_THROUGH = 3

    def __str__(self):
        if self.value == 3:
            return "fall-through"
        else:
            return self.name.lower()


class Block:
    def __init__(self, idn: int = None):
        self.id = idn
        self.children = {}

    def __str__(self):
        return f"BB{self.id}"

    def get_id(self):
        return self.id

    def update_id(self, idn: int):
        self.id = idn


class ConstantBlock(Block):
    def __init__(self, idn: int):
        super().__init__(idn)
        self.id = idn
        self.constants = {}

    def add_constant(self, instr: Instruction, constant: int):
        self.constants[constant] = instr

    def get_constant_id(self, constant: int) -> Instruction:
        return self.constants[constant]


class BasicBlock(Block):
    def __init__(self, idn: int = None, join: bool = False, while_block: bool = False):
        super().__init__(idn)
        self.dom_parents = set()
        self.join = join
        self.while_block = while_block
        self.instructions = {}
        self.instruction_order_list = []
        self.vars: dict = {}
        self.updated_vars = set()  # Used for adding var info to the graph
        self.phi_vars = set()
        self.parents: dict = {}
        self.children: {}
        self.existing_phis_instructions = {}
        self.dom_instructions = {}
        self.return_block = False
        self.array_assignments = {}  # model multiple dimension array as a single long array

    def update_join(self, join: bool):
        self.join = join

    def set_while(self, is_while: bool):
        self.while_block = is_while

    def is_while(self) -> bool:
        return self.while_block

    def is_cse(self, op: Operations = None, x: Instruction = None, y: Instruction = None):
        """
        Checks if the instruction is a common subexpression. If yes, returns the corresponding instruction id
        otherwise None
        :param op: operator for the instruction
        :param x: first instruction parameter or None
        :param y: second instruction parameter or None
        :return: instruction id or None
        """
        if (op, x, y) in self.dom_instructions:
            return self.dom_instructions[(op, x, y)]
        else:
            return None

    def add_new_instr_block(self, in_while, instr_id: int, op: Operations = None, x: Instruction = None, y: Instruction = None,
                            x_var: int = None, y_var: int = None) -> (
            int, bool):
        if in_while or (op, x, y) not in self.dom_instructions:
            inst = Instruction(instr_id, op, x, y, x_var, y_var)
            self.instructions[instr_id] = inst

            # For while blocks a phi instruction should be inserted at the beginning after
            # already existing phi instructions
            if op == Operations.PHI and self.while_block:
                insert_index = 0
                for i, instr in enumerate(self.instruction_order_list):
                    if instr.op != Operations.PHI:
                        insert_index = i
                        break
                self.instruction_order_list.insert(insert_index, inst)
            else:
                self.instruction_order_list.append(inst)

            # For phis in if the instruction number should be incremented immediately after the assignment so
            # make a list of those instructions so that they can be updated with the x and y later
            if op == Operations.PHI and not self.while_block:
                self.existing_phis_instructions[x_var] = inst

            # Add as a dominating instruction if applicable given the Operation (and not in while since they
            # will be added later)
            if op and op not in Operations.get_no_cse_instructions() and not in_while:
                self.add_dom_instruction(inst, op, x, y)

            return inst, False
        else:
            return self.dom_instructions[(op, x, y)], True

    def get_instructions(self) -> dict:
        return self.instructions

    def get_instruction_order_list(self) -> list[Instruction]:
        return self.instruction_order_list

    def get_vars(self) -> dict:
        return self.vars

    def add_var_assignment(self, var: int, instruction, update_var: bool = True, skip_return_check=False):
        if not self.return_block or skip_return_check:
            self.vars[var] = instruction
            if update_var:
                self.updated_vars.add(var)

    def copy_vars(self, new_vars: dict):
        self.vars = copy.deepcopy(new_vars)

    def add_parent(self, parent_block, parent_type: BlockRelation):
        self.parents[parent_block] = parent_type

    def remove_parent(self, parent_block: 'BasicBlock'):
        self.parents.pop(parent_block)

    def get_parents(self) -> dict:
        return self.parents

    def add_child(self, child_block: 'BasicBlock', child_type: BlockRelation):
        self.children[child_block] = child_type

    def remove_child(self, child_block: 'BasicBlock'):
        self.children.pop(child_block)

    def get_children(self) -> dict:
        return self.children

    def find_first_instr(self):
        if not self.instructions:
            return None
        return self.instruction_order_list[0]

    def update_instruction(self, instr: Instruction, x: Instruction = None, y: Instruction = None):
        instr: Instruction = self.instructions[instr.get_id()]
        if x:
            instr.x = x
        if y:
            instr.y = y

    def get_existing_phi_instruction(self, var: int) -> Instruction:
        """
        Returns the instruction id for the first already created phi instruction. Used for phi instructions in
        if-statements where the phi instructions need to be created immediately to get the correct instruction ids.
        :return: instruction id
        """
        instr = self.existing_phis_instructions[var]
        del self.existing_phis_instructions[var]
        return instr

    def available_exiting_phi_instruction(self, var: int) -> bool:
        if len(self.existing_phis_instructions) > 0 and var in self.existing_phis_instructions:
            return True
        return False

    def add_phi_var(self, phi_var: int):
        self.updated_vars.add(phi_var)
        self.phi_vars.add(phi_var)

    def get_phi_vars(self) -> set[int]:
        return self.phi_vars

    def get_dom_parents(self):
        return self.dom_parents

    def add_dom_parent(self, dom_parent: 'BasicBlock', in_while=False):
        self.dom_parents.add(dom_parent)
        if not in_while:
            self.copy_dom_instructions(dom_parent)

    def copy_dom_instructions(self, dom_parent):
        dom_parent_instructions = dom_parent.dom_instructions
        self.dom_instructions.update(dom_parent_instructions)

    def add_dom_instruction(self, instr: Instruction, op: Operations, x: Instruction, y: Instruction):
        if op != Operations.PHI:
            self.dom_instructions[(op, x, y)] = instr

    def get_dom_instruction(self):
        return self.dom_instructions

    def remove_instruction(self, instr: Instruction, index):
        del self.instructions[instr.get_id()]
        del self.instruction_order_list[index]

    def reset_instructions(self):
        self.instructions = {}
        self.instruction_order_list = []
        self.updated_vars = set()
        self.existing_phis_instructions = {}
        self.phi_vars = set()

    def set_as_return_block(self):
        self.return_block = True

    def is_return_block(self):
        return self.return_block

    def add_array(self, var: int, lengths: list[int]):
        array = None
        for length in reversed(lengths):
            array = [None] * length if array is None else [array.copy() for _ in range(length)]
        self.array_assignments[var] = array

    def get_array(self, token):
        return self.array_assignments[token]

    def get_array_assignment(self):
        return self.array_assignments

    def add_store_instruction(self, idn, x, x_var):
        instr = Instruction(idn, Operations.STORE, x=x, x_var=x_var)
        self.instructions[idn] = instr
        self.instruction_order_list.append(instr)

    def store_element_in_array(self, idn, array_token, element, indices):
        current_array = self.array_assignments[array_token]
        for index in indices[:-1]:
            current_array = current_array[index]
        current_array[indices[-1]] = element

        self.add_store_instruction(idn, -1, 400)


class Blocks:
    def __init__(self, baseSSA, initial_block):
        self.baseSSA = baseSSA
        self.id_count = 0
        self.constant_block = ConstantBlock(0)
        self.blocks_list: list[BasicBlock] = []
        self.current_block: BasicBlock = initial_block
        self.current_join_block = None
        self.leaf_joins = []
        self.leaf_joins_while = []
        self.instructions = {}
        self.removed_instructions = []

    def add_removed_instruction(self, instr: Instruction):
        self.removed_instructions.append(instr)

    def remove_instruction(self, idn: int):
        del self.instructions[idn]

    def add_new_instr(self, in_while, block: BasicBlock, instr_id: int, op: Operations = None, x: Instruction = None,
                      y: Instruction = None, x_var: int = None, y_var: int = None) -> int:
        """
        Adds a new instruction to the given block unless it is a common subexpression.
        :param y_var:
        :param x_var:
        :param in_while:
        :param block: block to add instruction to
        :param instr_id: instruction id
        :param op: operator
        :param x: first instruction parameter
        :param y: second instruction parameter
        :return: the instruction id of the new instruction or the common subexpression
        """
        if not block.is_return_block() or op == Operations.RET:
            instr, cse = block.add_new_instr_block(in_while, instr_id, op, x, y, x_var, y_var)
            if cse:
                self.baseSSA.decrease_id_count()
            else:
                self.instructions[instr_id] = instr
            return instr
        elif op != Operations.RET:
            self.baseSSA.decrease_id_count()

    def get_current_block(self) -> BasicBlock:
        return self.current_block

    def set_current_block(self, block: BasicBlock):
        self.current_block = block

    def get_constant_block(self) -> ConstantBlock:
        return self.constant_block

    def get_blocks_list(self) -> list[BasicBlock]:
        return self.blocks_list

    def get_new_block_id(self) -> int:
        self.id_count += 1
        return self.id_count

    def add_block(self, block: BasicBlock):
        block.update_id(self.get_new_block_id())
        self.blocks_list.append(block)
        self.current_block = block

    def remove_latest_block(self):
        latest_block = self.blocks_list.pop()
        parent_latest_block = list(latest_block.get_parents().keys())[0]
        parent_latest_block.remove_child(latest_block)
        self.current_block = self.blocks_list[-1]
        self.id_count -= 1

    def add_constant(self, constant: int):
        if constant not in self.constant_block.constants:
            instr_id = self.baseSSA.get_new_instr_id()
            instr = Instruction(id_count=instr_id, constant=constant)
            self.constant_block.add_constant(instr, constant)
            self.instructions[instr_id] = instr

    def get_constant_instr(self, constant: int) -> Instruction:
        return self.constant_block.get_constant_id(constant)

    def add_var_to_current_block(self, var: int, instruction: Instruction):
        self.current_block.add_var_assignment(var, instruction)

    def find_var_given_id(self, var: int) -> Instruction:
        return self.current_block.get_vars()[var]

    def update_current_join_block(self, block):
        self.current_join_block = block

    def get_current_join_block(self):
        return self.current_join_block

    def get_lowest_placed_leaf_join_block(self) -> BasicBlock:
        # The lowest placed is the one with the highest id
        highest_id = self.leaf_joins[0].get_id()
        highest_id_block = self.leaf_joins[0]

        for block in self.leaf_joins[1:]:
            current_id = block.get_id()

            if current_id > highest_id:
                highest_id = current_id
                highest_id_block = block

        self.leaf_joins.remove(highest_id_block)
        return highest_id_block

    def update_leaf_joins(self, join_block: BasicBlock):
        """
        Updates leaf join list by checking if a block is a leaf join block,
        i.e., whether it is not a child of another join block.
        :param join_block:
        """
        if self.leaf_joins and self.leaf_joins[-1] in join_block.get_parents():
            self.leaf_joins[-1] = join_block
        else:
            self.leaf_joins.append(join_block)

    def get_leaf_joins(self) -> list[BasicBlock]:
        return self.leaf_joins

