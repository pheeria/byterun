import dis
from frame import Frame
from typing import Optional


class VirtualMachineError(Exception):
    pass

class VirtualMachine:
    def __init__(self) -> None:
        self.frames = []
        self.frame: Optional[Frame] = None
        self.return_value = None
        self.last_exception = None

    def make_frame(self, code, callargs = {}, global_names = None, local_names = None) -> Frame:
        if global_names is not None and local_names is not None:
            local_names = global_names
        elif self.frames and self.frame:
            global_names = self.frame.global_names
            local_names = {}
        else:
            global_names = local_names = {
                    '__builtins__': __builtins__,
                    '__name__': '__main__',
                    '__doc__': None,
                    '__package__': None,
            }
        local_names.update(callargs)
        frame = Frame(code, global_names, local_names, self.frame)
        return frame

    def push_frame(self, frame):
        self.frames.append(frame)
        self.frame = frame

    def pop_frame(self):
        self.frames.pop()
        if self.frames:
            self.frame = self.frames[-1]
        else:
            self.frame = None

    def run_frame(self, frame: Frame):
        pass

    def run_code(self, code: dict, global_names = None, local_names = None) -> None:
        """ An entry point to execute code using the virtual machine."""
        frame = self.make_frame(code, global_names, local_names)
        self.run_frame(frame)

    def top(self):
        return self.frame.stack[-1]

    def pop(self):
        return self.frame.stack.pop()

    def push(self, *values):
        self.frame.stack.extend(values)

    def popn(self, n):
        """Pop a number of values from the value stack.
        A list of `n` values is returned, the deepest value first.
        """
        result = []
        if n:
            result = self.frame.stack[-n:]
            self.frame.stack[-n:] = []
        return result

    def parse_byte_and_args(self):
        frame: Frame = self.frame
        op_offset = frame.last_instruction
        bytecode = frame.code_object.co_code[op_offset]
        frame.last_instruction += 1
        bytename = dis.opname[bytecode]
        argument = []
        if bytecode >= dis.HAVE_ARGUMENT:
            arg = frame.code_object.co_code[frame.last_instruction:frame.last_instruction + 2]
            frame.last_instruction += 2
            arg_value = arg[0] + (arg[1] * 256)

            if bytecode in dis.hasconst:
                arg = frame.code_object.co_consts[arg_value]
            elif bytecode in dis.hasname:
                arg = frame.code_object.co_names[arg_value]
            elif bytecode in dis.haslocal:
                arg = frame.code_object.co_varnames[arg_value]
            elif bytecode in dis.hasjrel:
                arg = frame.last_instruction + arg_value
            else:
                arg = arg_value
            
            argument.append(arg)

        return bytename, argument
            
