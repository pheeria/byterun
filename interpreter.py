class Interpreter:
    def __init__(self) -> None:
        self.stack = []
        self.environment = {}

    def LOAD_VALUE(self, value: int) -> None:
        self.stack.append(value)

    def LOAD_NAME(self, name: str) -> None:
        value = self.environment[name]
        self.stack.append(value)

    def STORE_NAME(self, name: str) -> None:
        value = self.stack.pop()
        self.environment[name] = value

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
            instruction, argument = each
            if instruction == 'LOAD_VALUE':
                value = code['numbers'][argument]
                self.LOAD_VALUE(value)
            elif instruction == 'LOAD_NAME':
                value = code['names'][argument]
                self.LOAD_NAME(value)
            elif instruction == 'STORE_NAME':
                value = code['names'][argument]
                self.STORE_NAME(value)
            elif instruction == 'ADD_TWO_NUMBERS':
                self.ADD_TWO_NUMBERS()
            else:
                self.PRINT_ANSWER()


