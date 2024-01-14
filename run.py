import interpreter
from typing import List


def main() -> None:
    while True:
        user_input = input()

        if user_input.lower() == 'exit':
            break
        else:
            result: List[int] = interpreter.main(user_input)
            print(result)

        print(f"You entered: {user_input}")


if __name__ == "__main__":
    main()
