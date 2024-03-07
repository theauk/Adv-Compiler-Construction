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

    END = 10  # end of program
    BRA = 11  # branch to y
    BNE = 12  # branch to y on x not equal
    BEQ = 13  # branch to y on x equal
    BLE = 14  # branch to y on x less or equal
    BLT = 15  # branch to y on x less
    BGE = 16  # branch to y on x greater than or equal
    BGT = 17  # branch to y on x greater
    JSR = 18  # jump to subroutine x
    RET = 19  # return from subroutine

    READ = 20
    WRITE = 21
    WRITE_NL = 22

    KILL = 23
    BASE = 24

    def __str__(self) -> str:
        return f'{self.name}'.lower()

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def get_no_cse_instructions(cls):
        return {
            Operations.BEQ,
            Operations.BNE,
            Operations.BGE,
            Operations.BLE,
            Operations.BGT,
            Operations.BLT,
            Operations.BRA,
            Operations.PHI,
            Operations.READ,
            Operations.RET,
            Operations.KILL
        }
