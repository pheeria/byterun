class Frame:
    def __init__(self, code_object, global_names, local_names, previous_frame) -> None:
        self.code_object = code_object
        self.global_names = global_names
        self.local_names = local_names
        self.previous_frame = previous_frame

        if previous_frame:
            self.builtin_names = previous_frame.builtin_names
        else:
            self.builtin_names = local_names['__builtins__']
            if hasattr(self.builtin_names, '__dict__'):
                self.builtin_names = self.builtin_names.__dict__

        self.last_instruction = 0
        self.stack = []
        self.block_stack = []
