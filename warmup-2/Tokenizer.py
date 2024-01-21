from tokens import TokenType


class Tokenizer:  # TODO: comment out vars not in the simpler warm up language
    def __init__(self, debug=False):
        self.debug = debug

        self.tokens = {
            'number': TokenType.NUMBER,
            'identifier': TokenType.IDENTIFIER,

            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.TIMES,
            '/': TokenType.DIVISION,

            '==': TokenType.EQUAL,
            '!=': TokenType.NOT_EQUAL,
            '<': TokenType.LESS_THAN,
            '>': TokenType.GREATER_THAN,
            '<=': TokenType.LESS_THAN_OR_EQUAL,
            '>=': TokenType.GREATER_THAN_OR_EQUAL,

            '.': TokenType.PERIOD,
            ',': TokenType.COMMA,
            ';': TokenType.SEMICOLON,

            '(': TokenType.OPEN_PARENTHESIS,
            ')': TokenType.CLOSE_PARENTHESIS,
            '[': TokenType.OPEN_BRACKET,
            ']': TokenType.CLOSE_BRACKET,

            'let': TokenType.LET,
            'call': TokenType.CALL,

            'if': TokenType.IF,
            'then': TokenType.THEN,
            'else': TokenType.ELSE,
            'fi': TokenType.FI,

            'while': TokenType.WHILE,
            'do': TokenType.DO,
            'od': TokenType.OD,

            'return': TokenType.RETURN,

            'variable': TokenType.VAR,
            'array': TokenType.ARRAY,
            'void': TokenType.VOID,
            'function': TokenType.FUNCTION,
            'main': TokenType.MAIN,

            '<-': TokenType.ASSIGN,
            'computation': TokenType.COMPUTATION
        }
