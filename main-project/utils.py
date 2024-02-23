from blocks import BasicBlock, BlockRelation


class Utils:
    def __init__(self, blocks, baseSSA):
        self.blocks = blocks
        self.baseSSA = baseSSA

    def add_relationship(self, parent_block: BasicBlock, child_block: BasicBlock, relationship: BlockRelation):
        parent_block.add_child(child_block, relationship)
        child_block.add_parent(parent_block, relationship)

    def copy_vars(self, parent_block: BasicBlock, child_block: BasicBlock):
        child_block.vars = parent_block.vars.copy()

    def add_phi_instructions(self, block1: BasicBlock, block2: BasicBlock, var_set: set, already_added_vars: set,
                             join_block: BasicBlock):
        for child in var_set:
            if child not in already_added_vars:
                block1_child = block1.get_vars()[child]
                block2_child = block2.get_vars()[child]
                available_phi_instructions = join_block.get_available_phi_instruction()
                join_block.update_instruction(instr_idn=available_phi_instructions.get_id(), x=block2_child,
                                              y=block1_child)
                already_added_vars.add(child)

    def add_phis_if(self, if_block: BasicBlock, then_block: BasicBlock, else_block: BasicBlock):
        already_added_vars = set()
        join_block: BasicBlock = self.blocks.get_current_join_block()

        # Joining var that has been updated both in then and else
        intersection_then_else = then_block.get_updated_vars().intersection(else_block.get_updated_vars())
        self.add_phi_instructions(then_block, else_block, intersection_then_else, already_added_vars,
                                  join_block=join_block)

        # Joining var that has been updated in then
        intersection_if_then = if_block.get_updated_vars().intersection(then_block.get_updated_vars())
        self.add_phi_instructions(if_block, then_block, intersection_if_then, already_added_vars, join_block=join_block)

        # Joining var that has been updated in else
        intersection_if_else = if_block.get_updated_vars().intersection(else_block.get_updated_vars())
        self.add_phi_instructions(if_block, else_block, intersection_if_else, already_added_vars, join_block=join_block)

        if already_added_vars:
            join_block.update_join(True)

        self.update_var_table_for_block(join_block=join_block, then_block=then_block, else_block=else_block)

    def update_var_table_for_block(self, join_block, then_block, else_block):
        for key, value in then_block.get_vars().items():
            if key not in join_block.get_vars():
                join_block.add_var_assignment(key, value, update_var=False)

        for key, value in else_block.get_vars().items():
            if key not in join_block.get_vars():
                join_block.add_var_assignment(key, value, update_var=False)
