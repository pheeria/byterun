from interpreter import Interpreter

what_to_execute = {
    'instructions': [
        ('LOAD_VALUE', 0),
        ('LOAD_VALUE', 0),
        ('ADD_TWO_NUMBERS', None),
        ('LOAD_VALUE', 1),
        ('ADD_TWO_NUMBERS', None),
        ('PRINT_ANSWER', None),
    ],
    'numbers': [42, 23]
}

interpreter = Interpreter()
interpreter.run(what_to_execute)
