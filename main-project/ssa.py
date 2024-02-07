from operations import Operations


class BaseSSA:
    def __init__(self):
        self.id_count = -1

    def get_new_instr_id(self):
        self.id_count += 1
        return self.id_count


class Instruction:
    def __init__(self, id_count, op: Operations, x=None, y=None):
        self.id = id_count
        self.op = op
        self.x = x
        self.y = y

    def __str__(self):
        return f"{self.id}: {self.op} ({self.x}) ({self.y})"
