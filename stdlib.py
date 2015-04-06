"""Builtin functions for PSIL"""

from data import LLCode
from parse import Token, Reference

def pop(state):
    """Got tired of writing "state.env.stack" """
    return state.env.stack.pop()
    
def push(state, val):
    """See above"""
    state.env.stack.push(val)

class Duplicate(LLCode):
    """Duplicate the top item on the stack."""
    def run(self, state):
        print("dup: "+str(state.env.stack))
        push(state, state.env.stack.peek())
        
class Out(LLCode):
    """Sends top item on stack to stdout.
    
    "Proper" I/O will be handled later."""
    def run(self, state):
        print(pop(state))
        
class Math(LLCode):
    """Superclass for math operations with useful helper functions."""
    def grab(self, state):
        val2 = pop(state)
        val1 = pop(state)
        if isinstance(val1, data.Numeric) and isinstance(val2, data.Numeric):
            return (val1, val2)
        else:
            raise TypeError("Tried to multiply non-numerics")
        
        
class Multiply(Math):
    """Multiply the top two items from the stack"""
    def run(self, state):
        v1, v2 = self.grab(state)
        push(state, v1*v2)
        
class Subtract(Math):
    """subtract the second item on the stack by the top"""
    def run(self, state):
        v1, v2 = self.grab(state)
        push(state, v1-v2)
    
class Bind(LLCode):
    """Pull a value and a name off the stack and bind them in the namespace."""
    def run(self, state):
        val = pop(state)
        name = pop(state)
        ref = Reference(name.string)
        ns = state.env.deref(ref.prev())
        ns.bind(val, ref[-1])
        
builtins = {
    "def" : Bind(Token("#Builtin def#")),
    
    "dup" : Duplicate(Token("#Builtin dup#")),
    
    "out" : Out(Token("#Builtin out#")),
    
    "sub" : Subtract(Token("#Builtin sub#")),
    "mul" : Multiply(Token("#Builtin mul#"))
    
    }