import sys
import collections
import dis
from frame import Frame
from typing import Optional

Block = collections.namedtuple('Block', 'type, handler, stack_height')

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

        if why == 'exception':
            exception_type, value, traceback = self.last_exception
            e = exception_type(value)
            e.__traceback__ = traceback

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
            why = 'exception'
        return why

    def push_block(self, block_type, handler = None):
        stack_height = len(self.frame.stack)
        self.frame.block_stack.append(Block(block_type, handler, stack_height))

    def pop_block(self):
        return self.frame.block_stack.pop()

    def unwind_block(self, block):
        """Unwind the values on the data stack corresponding to a given block"""
        if block.type == 'except-handler':
            # The exception itself is on the stack as type, value and traceback
            offset = 3
        else:
            offset = 0

        while len(self.frame.stack) > block.stack_height + offset:
            self.pop()

        if block.type = 'except-handler':
            traceback, value, exception_type = self.popn(3)
            self.last_exception = exception_type, value, traceback

    def manage_block_stack(self, why):
        frame = self.frame
        block = frame.block_stack[-1]
        if block.type == 'loop' and why == 'continue':
            self.jump(self.return_value)
            why = None
            return why

        self.pop_block()
        self.unwind_block(block)

        if block.type == 'loop' and why == 'break':
            why = None
            self.jump(block.handler)
            return why

        if block.type in ['setup-except', 'finally'] and why == 'exception':
            self.push_block('except-handler')
            exception_type, value, traceback = self.last_exception
            self.push(traceback, value, exception_type)
            self.push(traceback, value, exception_type) # yes, twice
            why = None
            self.jump(block.handler)
            return why
        elif block.type == 'finally':
            if why in ['return', 'continue']:
                self.push(self.return_value)

            self.push(why)
            why = None
            self.jump(block.handler)
            return why
        return why
        
