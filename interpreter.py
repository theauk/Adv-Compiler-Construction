import string

DIGITS = "0123456789"
LETTERS = string.ascii_letters
DIGITS_LETTERS = DIGITS + LETTERS
PLUS = "+"
TIMES = "*"
OPEN_PAR = "("
CLOSING_PAR = ")"

user_inp = ""
current_inp = ''
index = 0


class Error:
    def __init__(self, name: str, desc: str):
        self.name = name
        self.desc = desc

    def get_error(self) -> str:
        return f"{self.name}: {self.desc}"


def next_inp():
    global current_inp
    global index

    # Skip spaces
    while index < len(user_inp) and user_inp[index].isspace():
        index += 1

    if index < len(user_inp):
        current_inp = user_inp[index]
        index += 1


def E() -> int:
    res: int = T()

    while current_inp == PLUS:
        next_inp()
        res += T()

    return res


def T() -> int:
    res: int = F()

    while current_inp == TIMES:
        next_inp()
        res *= F()

    return res


def F() -> int:
    res: int = 0

    if current_inp == OPEN_PAR:
        next_inp()
        res = E()
        if current_inp == CLOSING_PAR:
            next_inp()
        else:
            print("syntax_error")
    elif current_inp in DIGITS:
        res = int(current_inp)
        next_inp()
        while current_inp in DIGITS:
            res = 10 * res + int(current_inp)
            next_inp()
    else:
        print("syntax_error")

    return res


def parse() -> list[int]:
    results: list[int] = []
    while index < len(user_inp):
        next_inp()
        results.append(E())
    return results


def main(inp) -> list[int]:
    global user_inp
    user_inp = inp
    return parse()
