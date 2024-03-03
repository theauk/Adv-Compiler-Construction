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


class Instruction:
    def __init__(self, id_count, op: Operations = None, x: 'Instruction' = None, y: 'Instruction' = None, x_var=None,
                 y_var=None, constant=None):
        self.id = id_count
        self.op = op
        self.x = x
        self.y = y
        self.x_var = x_var
        self.y_var = y_var
        self.constant = constant

    def get_id(self):
        return self.id

    def set_constant(self, constant: int):
        self.constant = constant

    def __str__(self):
        if self.constant is not None:
            return f"{self.id}: const #{self.constant}"
        elif not self.x and not self.y and not self.op:
            return f"{self.id}: \<empty\>"
        elif not self.x and not self.y:
            return f"{self.id}: {self.op}"
        elif not self.y:
            return f"{self.id}: {self.op} ({self.x.get_id()})"
        else:
            return f"{self.id}: {self.op} ({self.x.get_id()}) ({self.y.get_id()})"

    def print_debug(self):
        if not self.x and not self.y and not self.op:
            return f"{self.id}: \<empty\>"
        elif not self.x and not self.y:
            return f"{self.id}: {self.op}"
        elif not self.y:
            return f"{self.id}: {self.op} ({self.x.get_id()}:{self.x_var if self.x_var else ''})"
        else:
            return f"{self.id}: {self.op} ({self.x.get_id()}:{self.x_var if self.x_var else ''}) ({self.y.get_id()}:{self.y_var if self.y_var else ''})"

    def __eq__(self, other):
        if isinstance(other, Instruction):
            return self.id == other.id
        return False

    def __lt__(self, other):
        if isinstance(other, Instruction):
            return self.id < other.id
        return NotImplemented

    def __hash__(self):
        return hash(self.id)
