from enum import Enum


class TokenType(Enum):
    INVALID = 0

    NUMBER = 1
    IDENTIFIER = 2

    PLUS = 3
    MINUS = 4
    TIMES = 5
    DIVISION = 6

    EQUAL = 7
    NOT_EQUAL = 8
    LESS_THAN = 9
    GREATER_THAN = 10
    LESS_THAN_OR_EQUAL = 11
    GREATER_THAN_OR_EQUAL = 12

    PERIOD = 13
    COMMA = 14
    SEMICOLON = 15

    OPEN_PARENTHESIS = 16
    CLOSE_PARENTHESIS = 17
    OPEN_BRACKET = 18
    CLOSE_BRACKET = 19

    LET = 20
    CALL = 21

    IF = 22
    THEN = 23
    ELSE = 24
    FI = 25

    WHILE = 26
    DO = 27
    OD = 28

    RETURN = 29

    VAR = 30
    ARRAY = 31
    VOID = 32
    FUNCTION = 33
    MAIN = 34

    ASSIGN = 35
    COMPUTATION = 36
