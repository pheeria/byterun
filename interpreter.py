from typing import Union, cast, Optional

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

    def parse_argument(self, code: dict, step: tuple[str, Optional[int]]) -> tuple[str, Union[str, int, None]]:
        """ Understand what the argument to each instruction means."""
        numbers = ['LOAD_VALUE']
        names = ['LOAD_NAME', 'STORE_NAME']
        instruction = step[0]
        argument = None
        if instruction in numbers:
            argument = code['numbers'][step[1]]
        elif instruction in names:
            argument = code['names'][step[1]]

        return instruction, argument


    def run(self, code: dict) -> None:
        for each in code['instructions']:
            instruction, argument = self.parse_argument(code, each)
            bytecode = getattr(self, instruction)
            if argument is None:
                bytecode()
            else:
                bytecode(argument)


