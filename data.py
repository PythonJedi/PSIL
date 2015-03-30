#! /usr/bin/python3
"""An outline of PSIL's type system and other internal data objects.

Author: Timothy Hewitt
Date: 2015-03-19"""

import parse

class Namespace:
    """Represents the type of a namespace, the catchall type."""
    def __init__(self, parent=None, stack=None):
        self.dict = {}
        self.parent = parent # "reversed" linked list of execution namespaces
        self.stack = stack
    
    def bind(self, ns, name):
        if not isinstance(ns, Namespace):
            raise TypeError(str(ns) +" is not a namespace.")
        else:
            self.dict[name]=ns
            ns.parent = None # references do not point back, solves aliasing
            
    def unbind(self, name):
        if name in self.dict:
            del self.dict[name]
        # fail quiet on deletion that doesn't exist
    
    def deref(self, name):
        nm = name.copy()
        val = self._search_up(name)
        val.name = nm # need unmodified copy
    
    def _search_up(self, name):
        if name[0] in self.dict:
            return self.dict[name[0]]._search_down(name.next())
        elif self.parent: # name not found, but not root namespace
            return self.parent.search(name) # Namespace.search(self.parent, name)
        else: # root namespace, name not found
            raise AttributeError(str(name)+" not found in namespace tree.")

    def _search_down(self, name):
        if name[0] in self.dict:
            return self.dict[name[0]]._search_down(name.next())
        else:
            raise AttributeError(str(name)+" not found in namespace tree.")

class Literal(Namespace):
    """Superclass for all the literal types in PSIL."""
    
class Code(Literal):
    """Type for a code literal."""
    def __init__(self, string, name=None):
        self.string = string
        self.instruction_list = None
        self.name = name
        
    def instructions(self):
        if not self.instruction_list:
            self.instruction_list = [i for i in parse.parse(self.string)]
        for i in self.instruction_list:
            yield i
            
class LLCode(Code):
    """Superclass for any code not implemented in PSIL
    
    This code is invoked by calling code.run(env) in the Execute instruction."""
    
class String(Literal):
    """Type for a string literal.
    
    I may work on unicode support, but it's not required for a proof of 
    concept."""
    
class Numeric(Literal):
    """Type superclass for numbers in PSIL."""
    
class Integer(Numeric):
    """Type for integer data in PSIL."""
    
class Float(Numeric):
    """Type for integer data in PSIL."""
    
class Stack:
    """Data stack that exists during execution of a PSIL program."""
    def __init__(self, init=None):
        if init and len(init[1].list) > init[0]: 
            # initialize a shallow copy of a stack with a smaller size
            self.list = init[1].list
            self.size = init[0]
        else:
            # new stack, original copy
            self.list = []
            self.size = 0
    
    def push(self, data):
        if not isinstance(data, Namespace):
            raise TypeError(str(data) + " is not a Namespace!")
        else:
            self.list.append(data)
            self.size += 1
    
    def pop(self):
        if self.size <= 0:
            raise IndexError("Tried to pop from empty stack")
        else:
            size -= 1
            return self.list.pop()
            
    def size(self):
        return self.size

        