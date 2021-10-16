from typing import Any
import types
import inspect

class Function:
    """
    Create a realistic function object, defining the things the interpreter expects.
    """
    __slots__ = [
            'func_code', 'func_name', 'func_defaults', 'func_globals',
            'func_locals', 'func_dict', 'func_closure',
            '__name__', '__dict__', '__doc__',
            '_vm', '_func',
    ]

    def __init__(self, name, code, globs, defaults, closure, vm) -> None:
        """You don't need to follow this closely to understand the interpreter."""
        self._vm = vm
        self.func_code = code
        self.func_name = self.__name__ = name or code.co_name
        self.func_defaults = tuple(defaults)
        self.func_globals = globs
        self.func_locals = self._vm.frame.f_locals
        self.__dict__ = {}
        self.func_closure = closure
        self.__doc__: Any = code.co_consts[0] if code.co_consts else None

        # Sometimes, we need a real Python function. This is for that.
        kw = {
                'argdefs': self.func_defaults,
        }
        if closure:
            kw['closure'] = tuple(make_cell(0) for _ in closure)
        self._func = types.FunctionType(code, globs, **kw)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """When calling a Function, make a new frame and run it."""
        callargs = inspect.getcallargs(self._func, *args, **kwargs)
        frame = self._vm.make_frame(self.func_code, callargs, self.func_globals, {})
        return self._vm.run_frame(frame)

def make_cell(value):
    """Create a real Python closure and grab a cell."""
    fn = (lambda x: lambda: x)(value)
    return fn.__closure__[0]
        
