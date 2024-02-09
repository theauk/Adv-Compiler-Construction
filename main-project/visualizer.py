from blocks import Blocks, BasicBlock, BlockRelation


class Visualizer:
    def __init__(self, blocks):
        self.blocks: Blocks = blocks

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

    def make_other_blocks(self):
        other_blocks: list[BasicBlock] = self.blocks.get_blocks_list()
        text = ''

        for block in other_blocks:
            text += f'bb{block.get_id()} [shape=record, label="<b>'
            text += f'join BB{block.get_id()} |' if block.join else f'BB{block.get_id()} | {{'
            block_texts = []
            for instruction_id in sorted(block.get_instructions().keys()):
                cur_instr = block.get_instructions()[instruction_id]
                block_texts.append(f'{str(cur_instr)}')
            text += '|'.join(block_texts)
            text += '}"];\n'

        return text

    def make_arrows(self):
        other_blocks: list[BasicBlock] = self.blocks.get_blocks_list()
        texts = []

        for block in other_blocks:
            parents = block.get_parents()
            for parent_block, parent_type in parents.items():
                if parent_type == BlockRelation.NORMAL:
                    texts.append(f'bb{parent_block.get_id()}:s -> bb{block.get_id()}:n ;')
                elif parent_type == BlockRelation.DOM:
                    texts.append(
                        f'bb{parent_block.get_id()}:s -> bb{block.get_id()}:n [color=blue, style=dotted, label="{str(parent_type)}"];')
                else:
                    texts.append(f'bb{parent_block.get_id()}:s -> bb{block.get_id()}:n [label="{str(parent_type)}"];')

        return '\n'.join(texts)

    def make_graph(self):
        constants = self.make_constants()
        other_blocks_text = self.make_other_blocks()
        solid_arrows = self.make_arrows()
        return 'digraph G {\n' + constants + other_blocks_text + solid_arrows + '\n}'
