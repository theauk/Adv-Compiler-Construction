from operations import Operations
from tokens import Tokens


class BaseSSA:
    def __init__(self):
        self.id_count = 0
        self.rel_op_to_instr = {
            Tokens.EQL_TOKEN: Operations.BEQ,
            Tokens.NEQ_TOKEN: Operations.BNE,
            Tokens.LSS_TOKEN: Operations.BGE,
            Tokens.GTR_TOKEN: Operations.BLE,
            Tokens.LEQ_TOKEN: Operations.BGT,
            Tokens.GEQ_TOKEN: Operations.BLT,
        }

    def get_new_instr_id(self) -> int:
        self.id_count += 1
        return self.id_count

    def get_cur_instr_id(self) -> int:
        return self.id_count

    def decrease_id_count(self):
        self.id_count -= 1

    def rel_op_to_instruction(self, rel_op: int) -> Operations:
        return self.rel_op_to_instr[rel_op]

    def get_no_cse_instructions(self):
        return self.rel_op_to_instr.update()


class Instruction:
    def __init__(self, id_count, op: Operations, x=None, y=None, x_var=None, y_var=None):
        self.id = id_count
        self.op = op
        self.x = x
        self.y = y
        self.x_var = x_var
        self.y_var = y_var

    def get_id(self):
        return self.id

    def __str__(self):
        if not self.x and not self.y and not self.op:
            return f"{self.id}: \<empty\>"
        elif not self.x and not self.y:
            return f"{self.id}: {self.op}"
        elif not self.y:
            return f"{self.id}: {self.op} ({self.x}:{self.x_var})"
        else:
            return f"{self.id}: {self.op} ({self.x}:{self.x_var}) ({self.y}:{self.y_var})"
