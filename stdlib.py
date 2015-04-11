"""Builtin functions for PSIL"""

from data import LLCode, Numeric, Reference
from parse import Token

def pop(state):
    """Got tired of writing "state.env.stack" """
    return state.env.stack.pop()
    
def push(state, val):
    """See above"""
    state.env.stack.append(val)

class Duplicate(LLCode):
    """Duplicate the top item on the stack.
    
    actually copies objects, but references are themselves copied, so 
    duplicating a reference and then manipulating the object the reference is 
    pointing to changes the object the second reference is pointed to as 
    well."""
    def __call__(self, state):
        val = state.env.stack.peek()
        new = (type(val))(val)
        push(state, new)
        
class Swap(LLCode):
    """Swaps the two items on the top of the stack."""
    def __call__(self, state):
        top, under = pop(state), pop(state)
        push(state, top)
        push(state, under)
        
class Out(LLCode):
    """Sends top item on stack to stdout.
    
    "Proper" I/O will be handled later."""
    def __call__(self, state):
        print(str(pop(state)))
        
class Get(LLCode):
    """Dereference a Reference."""
    def __call__(self, state):
        ref = pop(state)
        assert isinstance(ref, Reference)
        push(state, state.search(ref))
        
class Math(LLCode):
    """Superclass for math operations with useful helper functions."""
    def binary(self, state):
        """pull two items off and return them in the correct order."""
        val2 = pop(state)
        val1 = pop(state)
        # implicit deref
        if isinstance(val1, Reference):
            val1 = state.search(val1)
        if isinstance(val2, Reference):
            val2 = state.search(val2)
            
        if isinstance(val1, Numeric) and isinstance(val2, Numeric):
            return (val1, val2)
        else:
            raise TypeError("Tried to math non-numerics")
        
        
class Multiply(Math):
    """Multiply the top two items from the stack"""
    def __call__(self, state):
        v1, v2 = self.binary(state)
        push(state, v1*v2)
        
class Subtract(Math):
    """subtract the second item on the stack by the top"""
    def __call__(self, state):
        v1, v2 = self.binary(state)
        push(state, v1-v2)
    
class Bind(LLCode):
    """Pull a value and a name off the stack and bind them in the namespace."""
    def __call__(self, state):
        val = pop(state)
        name = pop(state)
        ns = state.search(name.previous())
        ns.bind(val, name.last)
        
builtins = {
    "def" : Bind(),
    "get" : Get(),
    
    "dup" : Duplicate(),
    "swap": Swap(),
    
    "out" : Out(),
    
    "sub" : Subtract(),
    "mul" : Multiply()
    
    }