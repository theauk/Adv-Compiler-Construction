from operations import Operations


class BaseSSA:
    def __init__(self):
        self.id_count = -1
        self.rel_op_to_instr = {
            '==': Operations.BEQ,
            '!=': Operations.BNE,
            '<': Operations.BGE,
            '>': Operations.BLE,
            '<=': Operations.BGT,
            '>=': Operations.BLT,
        }

    def get_new_instr_id(self):
        self.id_count += 1
        return self.id_count

    def rel_op_to_instruction(self, rel_op):
        return self.rel_op_to_instr[rel_op]


class Instruction:
    def __init__(self, id_count, op: Operations, x=None, y=None):
        self.id = id_count
        self.op = op
        self.x = x
        self.y = y

    def __str__(self):
        if not self.x and not self.y and not self.op:
            return f"{self.id}: <empty>"
        elif not self.x and not self.y:
            return f"{self.id}: {self.op}"
        elif not self.y:
            return f"{self.id}: {self.op} ({self.x})"
        else:
            return f"{self.id}: {self.op} ({self.x}) ({self.y})"
