# Check if parent block needs an empty instruction
        if len(self.blocks.get_current_block().get_instructions()) == 0:
            self.blocks.get_current_block().add_new_instr(self.baseSSA.get_new_instr_id())

        while_block = BasicBlock(while_block=True)
        self.utils.add_relationship(parent_block=self.blocks.get_current_block(), child_block=while_block,
                                    relationship=BlockRelation.NORMAL, copy_vars=True)
        self.blocks.add_block(while_block)

        self.blocks.update_current_join_block(while_block)

        left_side, rel_op_instr, right_side = self.relation()

        # make comparison instr
        cmp_instr_idn = while_block.add_new_instr(self.baseSSA.get_new_instr_id(), Operations.CMP, left_side,
                                                  right_side)
        # add the branch instr (branch instr added when known below)
        cmp_branch_to_instr = while_block.add_new_instr(self.baseSSA.get_new_instr_id(), op=rel_op_instr,
                                                        x=cmp_instr_idn)

        self.check_token(Tokens.DO_TOKEN)

        then_block = BasicBlock()
        self.utils.add_relationship(parent_block=while_block, child_block=then_block,
                                    relationship=BlockRelation.FALL_THROUGH, copy_vars=True)
        self.blocks.add_block(then_block)

        self.stat_sequence()

        self.utils.add_phis_while(while_block, then_block)

        self.check_token(Tokens.OD_TOKEN)

        if len(self.blocks.get_leaf_joins_while()) > 0:
            leaf_while: BasicBlock = self.blocks.get_lowest_leaf_join_block_while()
            leaf_while_parent = list(leaf_while.get_parents().keys())[0]
            # There are no instructions below od but in the "same" while block. Remove the branch block and branch
            # to the while above
            if len(leaf_while.get_instructions()) == 0:
                self.blocks.remove_latest_block()
                self.utils.add_relationship(parent_block=leaf_while_parent, child_block=while_block,
                                            relationship=BlockRelation.BRANCH)
                branch_block = leaf_while
            else:
                # There are instructions below od. Add a branch from that block to top of the current while.
                leaf_while.add_new_instr(instr_id=self.baseSSA.get_new_instr_id(), op=Operations.BRA,
                                         x=while_block.find_first_instr())
                self.utils.add_relationship(parent_block=leaf_while, child_block=while_block,
                                            relationship=BlockRelation.BRANCH)
                branch_block = leaf_while
        else:
            # new BB for branch
            branch_block = BasicBlock()
            self.utils.copy_vars(parent_block=while_block, child_block=branch_block, relationship=BlockRelation.BRANCH)
            self.blocks.add_block(branch_block)
            bra_instr = self.baseSSA.get_new_instr_id()
            then_block.add_new_instr(bra_instr, Operations.BRA, while_block.find_first_instr())
            self.utils.add_relationship(parent_block=then_block, child_block=while_block,
                                        relationship=BlockRelation.BRANCH)

        # Check if bra instruction should be inserted
        if len(branch_block.get_parents()) == 0:
            bra_instr = self.baseSSA.get_new_instr_id()
            then_block.add_new_instr(bra_instr, Operations.BRA, while_block.find_first_instr())
            self.utils.add_relationship(parent_block=then_block, child_block=while_block,
                                        relationship=BlockRelation.BRANCH)

        if len(branch_block.get_parents()) == 0:
            self.utils.add_relationship(parent_block=while_block, child_block=branch_block,
                                        relationship=BlockRelation.BRANCH)
        else:
            branch_block_parents = branch_block.get_parents()
            parent_block = list(branch_block_parents.keys())[0]
            self.utils.remove_relationship(parent_block, branch_block)
            self.utils.add_relationship(parent_block=parent_block, child_block=while_block,
                                        relationship=BlockRelation.BRANCH)

        if BlockRelation.BRANCH not in while_block.get_children().values():
            self.utils.add_relationship(parent_block=while_block, child_block=branch_block,
                                        relationship=BlockRelation.BRANCH)

        # TODO do this on second pass
        while_block.update_instruction(cmp_branch_to_instr, y=self.baseSSA.get_cur_instr_id() + 1)

        self.blocks.update_current_join_block(None)

        return