"""Builtin functions for PSIL"""

from data import LLCode
from parse import Dereference
    
class Bind(LLCode):
    """Pull a value and a name off the stack and bind them in the namespace."""
    def __init__(self):
        pass
        
    def run(self, env):
        val = env.stack.pop()
        name_s = env.stack.pop()
        # traverse the namespaces so that Namespace.bind() can be used
        