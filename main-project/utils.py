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
            self.copy_vars(parent_block, child_block)

    def copy_vars(self, parent_block: BasicBlock, child_block: BasicBlock):
        child_block.copy_vars(parent_block.get_vars())

    def create_phi_instruction(self, in_while, current_join_block, designator, x=None, y=None):
        if x and y or not current_join_block.is_while():
            current_join_block.add_phi_var(designator)
            instr = self.baseSSA.get_new_instr_id()
            self.blocks.add_new_instr(in_while, current_join_block, instr_id=instr, op=Operations.PHI, x=x, y=y,
                                      x_var=designator, y_var=designator)
            current_join_block.add_var_assignment(var=designator, instruction_number=instr,
                                                  while_block=current_join_block.is_while())
            return instr

    def add_phi_instructions(self, in_while, block1: BasicBlock, block2: BasicBlock, var_set: set,
                             already_added_vars: set,
                             join_block: BasicBlock):
        for child in var_set:
            block1_child = block1.get_vars()[child]
            block2_child = block2.get_vars()[child]
            if (block1_child, block2_child) not in already_added_vars:

                if block1_child != block2_child:
                    if join_block.available_exiting_phi_instruction():
                        phi_instruction = join_block.get_existing_phi_instruction()
                        join_block.update_instruction(instr_idn=phi_instruction, x=block1_child, y=block2_child)
                        join_block.add_var_assignment(var=child, instruction_number=phi_instruction)
                    else:
                        phi_instruction = self.create_phi_instruction(in_while, join_block, child, x=block1_child,
                                                                      y=block2_child)

                    join_block.add_var_assignment(var=child, instruction_number=phi_instruction)
                    already_added_vars.add((block1_child, block2_child))

    def add_phis_if(self, in_while, if_block: BasicBlock, then_block: BasicBlock, else_block: BasicBlock):
        already_added_vars = set()
        join_block: BasicBlock = self.blocks.get_current_join_block()

        if then_block.is_return_block():
            then_block = if_block
        if else_block.is_return_block():
            else_block = if_block

        # Joining var that has been updated both in then and else (or carried down from dominating blocks)
        then_vars = set(then_block.get_vars().keys())
        else_vars = set(else_block.get_vars().keys())
        intersection_then_else = then_vars.intersection(else_vars)
        self.add_phi_instructions(in_while, then_block, else_block, intersection_then_else, already_added_vars,
                                  join_block=join_block)

        # Remove unused phis due to return statement
        self.remove_unused_phis(join_block)

        if already_added_vars:
            join_block.update_join(True)
        else:
            # Redundant phis
            join_block.reset_instructions()

    def remove_unused_phis(self, join_block):
        unused_phis = []
        for i, instruction in enumerate(join_block.get_instruction_order_list()):
            if instruction.op == Operations.PHI and not instruction.x:
                unused_phis.append((instruction.get_id(), i))
        for idn, i in reversed(unused_phis):
            join_block.remove_instruction(idn, i)

    def add_phis_while(self, in_while, while_block: BasicBlock, then_block: BasicBlock):
        already_added_vars = set()

        # Check if the block to phi the while block with is not actually the original then block
        # but a block further down
        while_parents = while_block.get_parents()
        branch_parent_blocks = [obj for obj, enum in while_parents.items() if enum == BlockRelation.BRANCH]
        for block in branch_parent_blocks:
            if block.get_id() > then_block.get_id():
                then_block = block

        while_vars = set(while_block.get_vars().keys())
        then_vars = set(then_block.get_vars().keys())
        intersection_while_then = while_vars.intersection(then_vars)

        self.add_phi_instructions(in_while, block1=while_block, block2=then_block, var_set=intersection_while_then,
                                  already_added_vars=already_added_vars, join_block=while_block)

        if already_added_vars:
            while_block.update_join(True)

    def make_relation(self, if_block: BasicBlock, left_side, right_side, rel_op_instr, left_side_var, right_side_var,
                      in_while):
        # Check if potential cmp instr is a common subexpression
        cse_instr = if_block.is_cse(op=rel_op_instr, x=left_side, y=right_side)
        if not cse_instr:
            cmp_instr_idn = self.blocks.add_new_instr(in_while, if_block, self.baseSSA.get_new_instr_id(),
                                                      Operations.CMP, left_side, right_side, left_side_var,
                                                      right_side_var)
            # Add the branch instr (y added later when known)
            branch_instr_idn = self.blocks.add_new_instr(in_while, if_block, self.baseSSA.get_new_instr_id(),
                                                         op=rel_op_instr, x=cmp_instr_idn, x_var=left_side_var)
        else:
            # Common subexpression so only add the branch instruction
            branch_instr_idn = self.blocks.add_new_instr(in_while, if_block, self.baseSSA.get_new_instr_id(),
                                                         op=rel_op_instr, x=cse_instr, x_var=left_side_var)

        return branch_instr_idn

    def update_while(self, start_while_block: BasicBlock):
        # First pass to update phi instructions and propagate them + update bra instruction x value
        self.update_while_phis_and_bra(start_while_block)

        # Second pass to do cse
        self.update_while_cse(start_while_block)

    def update_while_phis_and_bra(self, start_while_block: BasicBlock):
        visited = {start_while_block}
        stack = []

        for child, relationship in start_while_block.get_children().items():
            if relationship == BlockRelation.FALL_THROUGH:
                stack.append(child)

        # Gather the instructions to update
        old_to_new_instr_ids = {}
        for i in start_while_block.get_instruction_order_list():
            if i.op == Operations.PHI:
                old_to_new_instr_ids[(i.x, i.x_var)] = i.id

        # Check instructions in the starting while block (except for the phi instructions where the updated variables
        # are coming from)
        for i in start_while_block.get_instructions().values():
            if i.op != Operations.PHI:
                if (i.x, i.x_var) in old_to_new_instr_ids:
                    start_while_block.update_instruction(i.id, x=old_to_new_instr_ids[(i.x, i.x_var)])
                if (i.y, i.y_var) in old_to_new_instr_ids:
                    start_while_block.update_instruction(i.id, y=old_to_new_instr_ids[(i.y, i.y_var)])

        # Keep going until we are back at the starting while block
        while stack:
            current_block = stack.pop()

            # Check if the instruction should be updated to match new phi value
            for i in current_block.get_instruction_order_list():
                original_i_x = i.x
                if (i.x, i.x_var) in old_to_new_instr_ids:
                    current_block.update_instruction(i.id, x=old_to_new_instr_ids[(i.x, i.x_var)])
                if (i.y, i.y_var) in old_to_new_instr_ids:
                    current_block.update_instruction(i.id, y=old_to_new_instr_ids[(i.y, i.y_var)])
                if i.op == Operations.PHI:
                    old_to_new_instr_ids[(original_i_x, i.x_var)] = i.id

            visited.add(current_block)

            for child_block, relationship in current_block.get_children().items():
                if relationship == BlockRelation.BRANCH:
                    # Update the branching instruction
                    branch_instr = current_block.get_instruction_order_list()[-1].get_id()
                    child_first_instr_id = child_block.find_first_instr()
                    current_block.update_instruction(branch_instr, x=child_first_instr_id)

                if child_block not in visited:
                    stack.append(child_block)

    def update_while_cse(self, start_while_block):
        visited = {start_while_block}
        stack = [start_while_block]
        removed_instructions = []
        phis = []

        # Keep going until we are back at the starting while block
        while stack:
            current_block: BasicBlock = stack.pop()

            # Copy instructions down if dominated
            for dom_parent in current_block.get_dom_parents():
                current_block.copy_dom_instructions(dom_parent)

            # Check if cse
            remove_instr = []
            for i, instruction in enumerate(current_block.get_instruction_order_list()):
                if instruction.op not in Operations.get_no_cse_instructions():
                    if (instruction.op, instruction.x, instruction.y) in current_block.get_dom_instruction():
                        cse_idn = current_block.get_dom_instruction()[(instruction.op, instruction.x, instruction.y)]
                        remove_instr.append((instruction.id, i, cse_idn))
                        removed_instructions.append(instruction.id)
                    else:
                        current_block.add_dom_instruction(instruction.id, instruction.op, instruction.x, instruction.y)
                elif instruction.op == Operations.PHI:
                    phis.append(instruction)

            # Remove cse instructions
            for (idn, i, cse_idn) in reversed(remove_instr):  # to not mess with indices
                current_block.remove_instruction(idn, i)
                # Update the table that keeps track of the var assignments so that the var points to the cse instruction
                for var, instr_idn in current_block.get_vars().items():
                    if instr_idn == idn:
                        current_block.add_var_assignment(var, cse_idn)

                # Check phis above
                for phi in phis:
                    if idn == phi.y:
                        phi.y = cse_idn

            visited.add(current_block)
            for child_block, relationship in current_block.get_children().items():
                if child_block not in visited:
                    stack.append(child_block)

        print("")

    def fix_while_branching(self, outer_while_blocks: list[BasicBlock]):
        for block in outer_while_blocks:
            for child_block, relationship in block.get_children().items():
                if relationship == BlockRelation.BRANCH:
                    # Update the branching instruction to the first instruction in the branch block
                    branch_instr = block.get_instruction_order_list()[-1].get_id()
                    child_first_instr_id = child_block.find_first_instr()
                    block.update_instruction(branch_instr, y=child_first_instr_id)
