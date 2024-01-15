# Global constants
DIGITS = "0123456789"
PLUS = "+"
MINUS = "-"
TIMES = "*"
DIVIDE = "/"
OPEN_PAR = "("
CLOSING_PAR = ")"

user_inp = ""
current_inp = ""
index = 0


class Error(Exception):
    def __init__(self, name: str, desc: str):
        super().__init__(f"{name}: {desc}")
        self.name = name
        self.desc = desc


def next_inp() -> None:
    """
    Updates the next input character and index. Skips extra whitespace.
    :return: None
    """
    global current_inp
    global index

    # Skip spaces
    while index < len(user_inp) and user_inp[index].isspace():
        index += 1

    if index < len(user_inp):
        current_inp = user_inp[index]
        index += 1


def expression() -> float:
    """
    Parses and evaluates an expression.
    :return: resulting value.
    """
    res: float = term()

    while current_inp == PLUS:
        next_inp()
        res += term()

    while current_inp == MINUS:
        next_inp()
        res -= term()

    return res


def term() -> float:
    """
    Parses and evaluates a term.
    :return: resulting value
    """
    res: float = factor()

    while current_inp == TIMES:
        next_inp()
        res *= factor()

    while current_inp == DIVIDE:
        next_inp()
        res /= factor()

    return res


def factor() -> float:
    """
    Parses and evaluates a factor in the expression.
    :return: resulting value
    :raises: SyntaxError
    """
    res: float = 0

    if current_inp == OPEN_PAR:
        next_inp()
        res = expression()
        if current_inp == CLOSING_PAR:
            next_inp()
        else:
            raise Error("SyntaxError", "Unclosed parenthesis")
    elif current_inp in DIGITS:
        res = int(current_inp)
        next_inp()
        while current_inp in DIGITS:
            res = 10 * res + int(current_inp)
            next_inp()
    else:
        raise Error("SyntaxError", "Invalid character")

    return res


def parse() -> list[str]:
    """
    Parses each expression separated by "."
    :return: list of computed results
    """
    results: list[str] = []
    while index < len(user_inp):
        try:
            next_inp()
            result = expression()
            # If applicable, convert float to int
            results.append(str(int(result)) if result == int(result) else str(result))
        except Error as e:
            results.append(str(e))
    return results


def main(inp) -> list[str]:
    global user_inp
    global index
    index = 0
    user_inp = inp
    return parse()
