class Reader:
    def __init__(self):
        self.text = ''
        self.index = 0

    def start(self):
        self.text = input()

    def get_next_inp(self):
        if self.index < len(self.text):
            inp = self.text[self.index]
            self.index += 1
            return inp
        else:
            return ''
