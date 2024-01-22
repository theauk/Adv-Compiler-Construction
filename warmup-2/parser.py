from tokenizer import Tokenizer


def main():
    tokenizer = Tokenizer()

    while True:
        result = tokenizer.get_next_token()
        print(result)


if __name__ == "__main__":
    main()
