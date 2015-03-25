#! /usr/bin/python3
"""An outline of PSIL's type system and other internal data objects.

Author: Timothy Hewitt
Date: 2015-03-19"""

import parse

class Namespace:
    """Represents the type of a namespace, the catchall type."""
    def __init__(self, parent=None, stack=None):
        self.dict = {}
        self.parent=parent # "reversed" linked list of execution namespaces
        self.stack = stack
    
    def bind(self, ns, name):
        if not isinstance(ns, (Namespace, Stack)):
            # Have to allow stacks for execution namespaces
            raise TypeError(str(ns) +" is not a namespace or stack.")
        else:
            self.dict[name]=ns
            ns.parent = None # references do not point back, solves aliasing
            
    def deref(self, name):
        if name in self.dict:
            return self.dict[name]
        else:
            raise AttributeError(name+" is not an attribute of "+str(self))
            
    def unbind(self, name):
        if name in self.dict:
            del self.dict[name]
        # fail quiet on deletion that doesn't exist
            
class Literal(Namespace):
    """Superclass for all the literal types in PSIL."""
    
class Code(Literal):
    """Type for a code literal."""
    def __init__(self, string, name=None):
        self.string = string
        self.instructions = None
        self.name = name
        
    def __getattr__(self, name):
        if name == "value":
            if not self.instructions:
                self.instructions = [i for i in parse.parse(self.string)]
            return self.instructions[:]
    
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
        if init and len(init[1].list > init[0]: 
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

        