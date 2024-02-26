import copy

from blocks import BasicBlock, BlockRelation
from operations import Operations


class Utils:
    def __init__(self, blocks, baseSSA):
        self.blocks = blocks
        self.baseSSA = baseSSA

    def add_relationship(self, parent_block: BasicBlock, child_block: BasicBlock, relationship: BlockRelation,
                         copy_vars=True):
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
        if x and y:
            current_join_block.add_phi_var(designator)
            instr = self.baseSSA.get_new_instr_id()
            self.blocks.add_new_instr(current_join_block, instr_id=instr, op=Operations.PHI, x=x, y=y,
                                      insert_at_beginning=current_join_block.is_while())
            current_join_block.add_var_assignment(designator, instr, False, current_join_block.is_while())
            return instr

    def add_phi_instructions(self, block1: BasicBlock, block2: BasicBlock, var_set: set, already_added_vars: set,
                             join_block: BasicBlock):
        for child in var_set:
            if child not in already_added_vars:
                block1_child = block1.get_vars()[child]
                block2_child = block2.get_vars()[child]

                if block1_child != block2_child:
                    if join_block.is_available_exiting_phi_instruction_number():
                        phi_instruction = join_block.get_existing_phi_instruction_number().get_id()
                        join_block.update_instruction(instr_idn=phi_instruction, x=block2_child, y=block1_child)
                        join_block.add_var_assignment(var=child, instruction_number=phi_instruction, update_var=True)
                    else:
                        phi_instruction = self.create_phi_instruction(join_block, child, x=block2_child, y=block1_child)

                    join_block.add_var_assignment(child, phi_instruction)
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

    def add_phis_while(self, while_block: BasicBlock, then_block: BasicBlock):
        already_added_vars = set()

        # Check for nested stmts where the upper while need to use the lower stmts
        while_parents = while_block.get_parents()
        branch_parent_blocks = [obj for obj, enum in while_parents.items() if enum == BlockRelation.BRANCH]
        for block in branch_parent_blocks:
            if block.get_id() > then_block.get_id():
                then_block = block

        while_vars = set(while_block.get_vars().keys())
        then_vars = set(then_block.get_vars().keys())
        intersection_while_then = while_vars.intersection(then_vars)

        self.add_phi_instructions(block1=while_block, block2=then_block, var_set=intersection_while_then,
                                  already_added_vars=already_added_vars, join_block=while_block)

        if already_added_vars:
            while_block.update_join(True)

    def make_relation(self, if_block: BasicBlock, left_side, right_side, rel_op_instr):
        # Check if potential cmp instr is cse
        cse_instr = if_block.is_cse(op=rel_op_instr, x=left_side, y=right_side)
        if not cse_instr:
            cmp_instr_idn = self.blocks.add_new_instr(if_block, self.baseSSA.get_new_instr_id(), Operations.CMP,
                                                      left_side, right_side)
            # add the branch instr (branch instr y added when known later)
            branch_instr_idn = self.blocks.add_new_instr(if_block, self.baseSSA.get_new_instr_id(), op=rel_op_instr,
                                                         x=cmp_instr_idn)
        else:
            branch_instr_idn = self.blocks.add_new_instr(if_block, self.baseSSA.get_new_instr_id(), op=rel_op_instr,
                                                         x=cse_instr)

        return branch_instr_idn

    def fix_phi_and_outer_while_bra(self):
        blocks_list: list[BasicBlock] = self.blocks.get_blocks_list()

        for block in blocks_list:
            if block.is_while():

                # Update the branching instruction
                branch_instr = block.get_instruction_order_list()[-1].get_id()

                for child, relation_type in block.get_children().items():
                    if relation_type == BlockRelation.BRANCH:
                        child_first_instr_id = child.find_first_instr()
                        block.update_instruction(branch_instr, y=child_first_instr_id)
                    elif relation_type == BlockRelation.FALL_THROUGH:
                        self.update_phis_while(block, child)

    def update_phis_while(self, start_while_block: BasicBlock, fall_through_child: BasicBlock):
        visited = {start_while_block}
        path = []
        stack = [fall_through_child]

        old_to_new_instr_ids = {}
        for i in start_while_block.get_instructions().values():
            if i.op == Operations.PHI:
                old_to_new_instr_ids[i.y] = i.id

        for i in start_while_block.get_instructions().values():
            if i.op != Operations.PHI:
                if i.x in old_to_new_instr_ids:
                    start_while_block.update_instruction(i.id, x=old_to_new_instr_ids[i.x])
                if i.y in old_to_new_instr_ids:
                    start_while_block.update_instruction(i.id, y=old_to_new_instr_ids[i.y])

        while stack:
            current_block = stack.pop()

            for i in current_block.get_instructions().values():
                if i.x in old_to_new_instr_ids:
                    current_block.update_instruction(i.id, x=old_to_new_instr_ids[i.x])
                if i.y in old_to_new_instr_ids:
                    current_block.update_instruction(i.id, y=old_to_new_instr_ids[i.y])

            visited.add(current_block)
            path.append(current_block)

            for child_block in current_block.get_children().keys():
                if child_block not in visited:
                    stack.append(child_block)
