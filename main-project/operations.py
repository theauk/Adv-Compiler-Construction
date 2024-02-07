from enum import Enum


class Operations(Enum):
    ADD = 1
    SUB = 2
    MUL = 3
    DIV = 4
    CMP = 5

    ADDA = 6
    LOAD = 7
    STORE = 8
    PHI = 9

    END = 10
    BRA = 11
    BNE = 12
    BEQ = 13
    BLE = 14
    BLT = 15
    BGE = 16
    BGT = 17
    JSR = 18
    RET = 19

    READ = 20
    WRITE = 21
    WRITE_NL = 22

    def __str__(self) -> str:
        return f'{self.name}'.lower()

    def __repr__(self) -> str:
        return self.__str__()
