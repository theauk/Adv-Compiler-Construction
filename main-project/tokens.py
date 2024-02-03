class Tokens:
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

    INPUT_NUM_TOKEN = 220
    OUTPUT_NUM_TOKEN = 221
    OUTPUT_NEW_LINE_TOKEN = 222

    EOF_TOKEN = 255

    @classmethod
    def get_index_to_id_dict(cls):
        return {value: name for name, value in cls.__dict__.items() if
                not name.startswith("__") and not callable(getattr(cls, name)) and not isinstance(value, dict)}


class Strings:
    SYMBOLS = {
        '+': Tokens.PLUS_TOKEN,
        '-': Tokens.MINUS_TOKEN,
        '*': Tokens.TIMES_TOKEN,
        '/': Tokens.DIV_TOKEN,

        '==': Tokens.EQL_TOKEN,
        '!=': Tokens.NEQ_TOKEN,
        '<': Tokens.LSS_TOKEN,
        '>': Tokens.GTR_TOKEN,
        '<=': Tokens.LEQ_TOKEN,
        '>=': Tokens.GEQ_TOKEN,

        '.': Tokens.PERIOD_TOKEN,
        ',': Tokens.COMMA_TOKEN,
        ';': Tokens.SEMI_TOKEN,

        '(': Tokens.OPEN_PAREN_TOKEN,
        ')': Tokens.CLOSE_PAREN_TOKEN,
        '[': Tokens.OPEN_BRACKET_TOKEN,
        ']': Tokens.CLOSE_BRACKET_TOKEN,
        '}': Tokens.END_TOKEN,
        '{': Tokens.BEGIN_TOKEN,

        '<-': Tokens.BECOMES_TOKEN,
    }

    KEYWORDS = {
        'let': Tokens.LET_TOKEN,
        'call': Tokens.CALL_TOKEN,

        'if': Tokens.IF_TOKEN,
        'then': Tokens.THEN_TOKEN,
        'else': Tokens.ELSE_TOKEN,
        'fi': Tokens.FI_TOKEN,

        'while': Tokens.WHILE_TOKEN,
        'do': Tokens.DO_TOKEN,
        'od': Tokens.OD_TOKEN,

        'return': Tokens.RETURN_TOKEN,

        'var': Tokens.VAR_TOKEN,
        'array': Tokens.ARR_TOKEN,
        'void': Tokens.VOID_TOKEN,
        'function': Tokens.FUNC_TOKEN,
        'procedure': Tokens.PROC_TOKEN,
        'main': Tokens.MAIN_TOKEN,

        'InputNum': Tokens.INPUT_NUM_TOKEN,
        'OutputNum': Tokens.OUTPUT_NUM_TOKEN,
        'OutputNewLine': Tokens.OUTPUT_NEW_LINE_TOKEN
    }
