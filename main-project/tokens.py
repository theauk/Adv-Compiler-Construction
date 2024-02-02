from enum import Enum


class Tokens(Enum):
    ERROR_TOKEN = 0

    TIMES_TOKEN = 1
    DIV_TOKEN = 2

    PLUS_TOKEN = 11
    MINUS_TOKEN = 12

    EQL_TOKEN = 20
    NEQ_TOKEN = 21
    LSS_TOKEN = 22
    GEQ_TOKEN = 23
    LEQ_TOKEN = 24
    GTR_TOKEN = 25

    PERIOD_TOKEN = 30
    COMMA_TOKEN = 31
    OPEN_BRACKET_TOKEN = 32
    CLOSE_BRACKET_TOKEN = 34
    CLOSE_PAREN_TOKEN = 35

    BECOMES_TOKEN = 40
    THEN_TOKEN = 41
    DO_TOKEN = 42

    OPEN_PAREN_TOKEN = 50

    NUMBER = 60
    IDENT = 61

    SEMI_TOKEN = 70

    END_TOKEN = 80
    OD_TOKEN = 81
    FI_TOKEN = 82

    ELSE_TOKEN = 90

    LET_TOKEN = 100
    CALL_TOKEN = 101
    IF_TOKEN = 102
    WHILE_TOKEN = 103
    RETURN_TOKEN = 104

    VAR_TOKEN = 110
    ARR_TOKEN = 111
    VOID_TOKEN = 112
    FUNC_TOKEN = 113
    PROC_TOKEN = 114

    BEGIN_TOKEN = 150
    MAIN_TOKEN = 200
    EOF_TOKEN = 255


