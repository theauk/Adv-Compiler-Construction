import interpreter


def main() -> None:
    while True:
        user_input = input()

        if user_input.lower() == 'exit':
            break
        else:
            result: list[str] = interpreter.main(user_input)
            print(*result, sep='\n')


if __name__ == "__main__":
    main()
