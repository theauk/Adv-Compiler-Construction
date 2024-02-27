class FileReader:
    def __init__(self, file_name):
        try:
            self.file = open(file_name, 'r')
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{file_name}' does not exist.")

        self.current_char = self.file.read(1)

    def get_next(self):
        if not self.current_char:
            self.close()
            return ''

        return_char = self.current_char
        self.current_char = self.file.read(1)
        return return_char

    def error(self, error_msg: str):
        print(f"Error: {error_msg}")

    def close(self):
        self.file.close()
