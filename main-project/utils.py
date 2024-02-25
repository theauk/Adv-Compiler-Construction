import copy

from blocks import BasicBlock, BlockRelation
from operations import Operations


class Utils:
    def __init__(self, blocks, baseSSA):
        self.blocks = blocks
        self.baseSSA = baseSSA

    def add_relationship(self, parent_block: BasicBlock, child_block: BasicBlock, relationship: BlockRelation,
                         copy_vars=False):
        parent_block.add_child(child_block, relationship)
        child_block.add_parent(parent_block, relationship)
        if copy_vars:
            self.copy_vars(parent_block, child_block, relationship)

    def remove_relationship(self, parent_block: BasicBlock, child_block: BasicBlock):
        parent_block.remove_child(child_block)
        child_block.remove_parent(parent_block)

    def copy_vars(self, parent_block: BasicBlock, child_block: BasicBlock, relationship: BlockRelation):
        child_block.vars = copy.deepcopy(parent_block.vars)
        if relationship == BlockRelation.BRANCH or relationship == BlockRelation.FALL_THROUGH:
            child_block.initialize_vars(parent_block.get_vars())

    def create_phi_instruction(self, current_join_block, designator, x=None, y=None):
        current_join_block.add_phi_var(designator)
        instr = self.baseSSA.get_new_instr_id()
        if x and y:
            current_join_block.add_new_instr(instr_id=instr, op=Operations.PHI, x=x, y=y,
                                             start=current_join_block.is_while())
        else:
            current_join_block.add_new_instr(instr_id=instr, op=Operations.PHI, start=current_join_block.is_while())
        current_join_block.add_var_assignment(designator, instr, False, current_join_block.is_while())

    def add_phi_instructions(self, block1: BasicBlock, block2: BasicBlock, var_set: set, already_added_vars: set,
                             join_block: BasicBlock):
        for child in var_set:
            if child not in already_added_vars:
                block1_child = block1.get_vars()[child]
                block2_child = block2.get_vars()[child]

                if block1_child != block2_child:
                    if join_block.is_available_exiting_phi_instruction_number():
                        phi_instructions = join_block.get_existing_phi_instruction_number()
                        join_block.update_instruction(instr_idn=phi_instructions.get_id(), x=block2_child,
                                                      y=block1_child)
                        join_block.add_var_assignment(var=child, instruction_number=phi_instructions.get_id(),
                                                      update_var=True)
                    else:
                        self.create_phi_instruction(join_block, child, x=block2_child, y=block1_child)

                    already_added_vars.add(child)

    def add_phis_if(self, then_block: BasicBlock, else_block: BasicBlock):
        already_added_vars = set()
        join_block: BasicBlock = self.blocks.get_current_join_block()

        # Joining var that has been updated both in then and else
        then_vars = set(then_block.get_vars().keys())
        else_vars = set(else_block.get_vars().keys())
        intersection_then_else = then_vars.intersection(else_vars)
        self.add_phi_instructions(then_block, else_block, intersection_then_else, already_added_vars,
                                  join_block=join_block)

        if already_added_vars:
            join_block.update_join(True)

        # self.update_var_table_for_block(join_block=join_block, then_block=then_block, else_block=else_block)

    def add_phis_while(self, while_block, then_block):
        already_added_vars = set()
        while_vars = set(while_block.get_vars().keys())
        then_vars = set(then_block.get_vars().keys())
        intersection_while_then = while_vars.intersection(then_vars)

        self.add_phi_instructions(block1=while_block, block2=then_block, var_set=intersection_while_then,
                                  already_added_vars=already_added_vars, join_block=while_block)

        if already_added_vars:
            while_block.update_join(True)
