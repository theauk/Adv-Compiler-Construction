from blocks import Blocks, BasicBlock, BlockRelation


class Visualizer:
    def __init__(self, blocks, symbol_table, show_vars=False):
        self.blocks: Blocks = blocks
        self.symbol_table = symbol_table
        self.show_vars = show_vars

    def make_constants(self):
        constant_complete_text = 'bb0 [shape=record, label="<b>BB0 | {'
        constant_block_constants = self.blocks.get_constant_block().constants
        sorted_dict = dict(sorted(constant_block_constants.items(), key=lambda x: x[1]))
        constants_text = []

        for constant, idn in sorted_dict.items():
            constants_text.append(f'{idn}: const #{constant}')
        constant_complete_text += '|'.join(constants_text)
        constant_complete_text += '}"];\n'
        return constant_complete_text

    def make_main_blocks(self):
        other_blocks: list[BasicBlock] = self.blocks.get_blocks_list()
        text = ''

        for block in other_blocks:
            text += f'bb{block.get_id()} [shape=record, label="<b>'
            text += f'join BB{block.get_id()} | {{' if block.join else f'BB{block.get_id()} | {{'
            block_texts = []
            for instruction_id in sorted(block.get_instructions().keys()):
                cur_instr = block.get_instructions()[instruction_id]
                block_texts.append(f'{str(cur_instr)}')
            text += '|'.join(block_texts)
            text += '}'

            block_vars = block.get_vars()
            filtered_vars = {key: value for key, value in block_vars.items() if key in block.updated_vars}
            if self.show_vars and filtered_vars:
                text += '| {'
                formatted_strings = [f"{self.symbol_table[key]}: {value}" for key, value in filtered_vars.items()]
                text += ' | '.join(formatted_strings)
                text += '}'

            text += '"];\n'

        return text

    def make_arrows(self):
        other_blocks: list[BasicBlock] = self.blocks.get_blocks_list()
        instrs = []
        branches = []
        doms = []

        for block in other_blocks:
            parents = block.get_parents()
            for parent_block, parent_type in parents.items():
                if parent_type == BlockRelation.NORMAL:
                    instrs.append(f'bb{parent_block.get_id()}:s -> bb{block.get_id()}:n ;')
                elif parent_type == BlockRelation.DOM:
                    doms.append(
                        f'bb{parent_block.get_id()}:s -> bb{block.get_id()}:n [color=blue, style=dotted, label="{str(parent_type)}"];')
                else:
                    instrs.append(f'bb{parent_block.get_id()}:s -> bb{block.get_id()}:n [label="{str(parent_type)}"];')

        return '\n'.join(instrs) + '\n'.join(branches) + '\n'.join(doms)

    def make_graph(self):
        constants = self.make_constants()
        other_blocks_text = self.make_main_blocks()
        solid_arrows = self.make_arrows()
        return 'digraph G {\n' + constants + other_blocks_text + solid_arrows + '\n}'
