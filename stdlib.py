"""Builtin functions for PSIL"""

from data import LLCode
import parse
    
class Bind(LLCode):
    """Pull a value and a name off the stack and bind them in the namespace."""
    def __init__(self):
        pass
        
    def run(self, state):
        val = state.env.stack.pop()
        name = state.env.stack.pop()
        ns = state.env.deref(name.prev())
        ns.bind(
        