class Block:
    def __init__(self, id_count=None, parent=None):
        self.id = id_count
        self.parent = parent

    def __str__(self):
        return f"BB{self.id}"

    def update_id(self, id_count):
        self.id = id_count


class ConstantBlock(Block):
    def __init__(self, id_count):
        super().__init__(id_count)
        self.id = id_count
        self.constants = {}

    def add_constant(self, instruction_id, constant):
        if constant not in self.constants:
            self.constants[constant] = instruction_id


class BasicBlock(Block):
    def __init__(self, id_count=None, parent=None):
        super().__init__(id_count, parent)
        self.dom = []
        self.branch = None
        self.fall_through = None
        self.instructions = []
        self.join = False

    def add_fall_through(self, then_block):
        self.fall_through = then_block

    def add_branch(self, else_block):
        self.branch = else_block


class Blocks:
    def __init__(self):
        self.id_count = 0
        self.constant_block = ConstantBlock(0)
        self.blocks_list = [self.constant_block]
        self.current_block = self.constant_block

    def get_current_block(self):
        return self.current_block

    def add_block(self, block):
        block.update_id(self.get_new_block_id())
        self.blocks_list.append(block)
        self.current_block = block

    def get_new_block_id(self):
        self.id_count += 1
        return self.id_count

    def add_constant(self, id_count, constant):
        self.constant_block.add_constant(id_count, constant)
