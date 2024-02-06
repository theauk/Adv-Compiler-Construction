class Visualizer:
    def __init__(self, blocks):
        self.blocks = blocks.blocks_list

    def make_constants_text(self):
        constant_complete_text = 'bb0 [shape=record, label="<b>BB0 | {'
        constant_block = self.blocks[0].constants
        sorted_dict = dict(sorted(constant_block.items(), key=lambda x: x[1]))
        constants_text = []

        for constant, idn in sorted_dict.items():
            constants_text.append(f'{idn}: const #{constant}')
        constant_complete_text += '|'.join(constants_text)
        constant_complete_text += '}"];'
        return constant_complete_text

    def make_graph(self):
        text = self.make_constants_text()
        return text
