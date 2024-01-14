DIGITS = "0123456789"
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS_LETTERS = DIGITS + LETTERS
PLUS = "+"
TIMES = "*"
OPEN_PAR = "("
CLOSING_PAR = ")"

user_inp = ""
current_inp = ''
index = 0
results = []


class Error:
    def __init__(self, name: str, desc: str):
        self.name = name
        self.desc = desc

    def get_error(self) -> str:
        return f"{self.name}: {self.desc}"


def next_inp():
    global current_inp
    global index
    global results
    current_inp = user_inp[index]
    index += 1
    print("New token: ", current_inp)


def E() -> int:
    print("in E")
    res: int = T()

    while current_inp == PLUS:
        next_inp()
        res += T()

    return res


def T() -> int:
    print("in T")
    res: int = F()

    while current_inp == TIMES:
        next_inp()
        res *= F()

    return res


def F() -> int:
    print("in F")
    res: int = 0

    if current_inp == OPEN_PAR:
        next_inp()
        res = E()
        if current_inp == CLOSING_PAR:
            next_inp()
        else:
            print("syntax_error")
    elif current_inp in DIGITS_LETTERS:
        res = int(current_inp)
        next_inp()
        while current_inp in DIGITS_LETTERS:
            res = 10 * res + int(current_inp)
            next_inp()
    else:
        print("syntax_error")

    return res


def parse() -> list[int]:
    global results
    while index < len(user_inp):
        next_inp()
        results.append(E())
    print("result: ", results)
    return results


def main(inp) -> list[int]:
    global user_inp
    user_inp = inp
    return parse()
