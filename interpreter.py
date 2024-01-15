import string

DIGITS = "0123456789"
LETTERS = string.ascii_letters
DIGITS_LETTERS = DIGITS + LETTERS
PLUS = "+"
MINUS = "-"
TIMES = "*"
DIVIDE = "/"
OPEN_PAR = "("
CLOSING_PAR = ")"

user_inp = ""
current_inp = ''
index = 0


class Error(Exception):
    def __init__(self, name: str, desc: str):
        super().__init__(f"{name}: {desc}")
        self.name = name
        self.desc = desc


def next_inp():
    global current_inp
    global index

    # Skip spaces
    while index < len(user_inp) and user_inp[index].isspace():
        index += 1

    if index < len(user_inp):
        current_inp = user_inp[index]
        index += 1


def E() -> float:
    res: float = T()

    while current_inp == PLUS:
        next_inp()
        res += T()

    while current_inp == MINUS:
        next_inp()
        res -= T()

    return res


def T() -> float:
    res: float = F()

    while current_inp == TIMES:
        next_inp()
        res *= F()

    while current_inp == DIVIDE:
        next_inp()
        res /= F()

    return res


def F() -> float:
    res: float = 0

    if current_inp == OPEN_PAR:
        next_inp()
        res = E()
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
    results: list[str] = []
    while index < len(user_inp):
        try:
            next_inp()
            result = E()
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
