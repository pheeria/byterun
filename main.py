from interpreter import Interpreter

what_to_execute = {
    'instructions': [
        ('LOAD_VALUE', 0),
        ('STORE_NAME', 0),
        ('LOAD_VALUE', 1),
        ('STORE_NAME', 1),
        ('LOAD_NAME', 0),
        ('LOAD_NAME', 1),
        ('ADD_TWO_NUMBERS', None),
        ('PRINT_ANSWER', None),
    ],
    'numbers': [42, 9],
    'names': ['meaning', 'crisis'],
}

interpreter = Interpreter()
interpreter.run(what_to_execute)
