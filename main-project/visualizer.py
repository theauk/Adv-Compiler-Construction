from blocks import Blocks, BasicBlock, ParentType


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
            text += f'join\nBB{block.get_id()} |' if block.join else f'BB{block.get_id()} | {{'
            block_texts = []
            for instruction in sorted(block.get_instructions().values()):
                block_texts.append(f'{str(instruction)}')
            text += '|'.join(block_texts)
            text += '}"];\n'

        return text

    def make_solid_arrows(self):
        other_blocks: list[BasicBlock] = self.blocks.get_blocks_list()
        texts = []

        for block in other_blocks:
            parents = block.get_parents()
            for parent_block, parent_type in parents.items():
                if parent_type != ParentType.NORMAL:
                    texts.append(f'bb{parent_block.get_id()}:s -> bb{block.get_id()}:n [label="{str(parent_type)}"];')
                else:
                    texts.append(f'bb{parent_block.get_id()}:s -> bb{block.get_id()}:n ;')

        return '\n'.join(texts)

    def make_dom_arrows(self):
        return '\n'

    def make_graph(self):
        constants = self.make_constants()
        other_blocks_text = self.make_other_blocks()
        solid_arrows = self.make_solid_arrows()
        dom_arrows = self.make_dom_arrows()
        return 'digraph G {\n' + constants + other_blocks_text + solid_arrows + dom_arrows + '}'
