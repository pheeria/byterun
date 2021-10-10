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

