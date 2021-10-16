import sys
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
        """Run a frame until it returns (somehow).
        Exceptions are raised, the return value is returned."""
        self.push_frame(frame)
        while True:
            bytename, argument = self.parse_byte_and_args()
            why = self.dispatch(bytename, argument)

            while why and frame.block_stack:
                why = self.manage_block_stack(why)

            if why:
                break

        self.pop_frame()

        if why == 'Exception':
            exc, value, tb = self.last_exception
            e = exc(value)
            e.__traceback__ = tb

        return self.return_value

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
            
    def dispatch(self, bytename, argument):
        """ Dispatch by bytename to the corresponding methods.
        Exceptions are caught and set on the virtual machine."""

        # When later unwinding the block stack,
        # we need to keep track of why we are doing it
        why = None
        try:
            bytecode_fn = getattr(self, f'byte_{bytename}', None)
            if bytecode_fn is None:
                if bytename.startsWith('UNARY_'):
                    self.unary_operator(bytename[6:])
                elif bytename.startsWith('BINARY_'):
                    self.binary_operator(bytename[7:])
                else:
                    raise VirtualMachineError(f'Unsupported bytecode type: {bytename}')
            else:
                why = bytecode_fn(*argument)
        except:
            # deal with exceptions encountered while executing the operation
            self.last_exception = sys.exc_info()[:2] + (None,)
            why = 'Exception'
        return why

