class Interpreter:
    def __init__(self) -> None:
        self.stack = []

    def LOAD_VALUE(self, value: int) -> None:
        self.stack.append(value)

    def ADD_TWO_NUMBERS(self) -> None:
        first = self.stack.pop()
        second = self.stack.pop()
        total = first + second
        self.stack.append(total)

    def PRINT_ANSWER(self) -> None:
        value = self.stack.pop()
        print(value)

    def run(self, code: dict) -> None:
        for each in code['instructions']:
            instruction = each[0]
            if instruction == 'LOAD_VALUE':
                value = code['numbers'][each[1]]
                self.LOAD_VALUE(value)
            elif instruction == 'ADD_TWO_NUMBERS':
                self.ADD_TWO_NUMBERS()
            else:
                self.PRINT_ANSWER()


