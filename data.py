#! /usr/bin/python3
"""An outline of PSIL's type system and other internal data objects.

Author: Timothy Hewitt
Date: 2015-03-19"""

import parse

class Namespace:
    """Represents the type of a namespace, the catchall type."""
    def __init__(self, stack=None, parent=None, **kwdarg):
        if isinstance(stack, Namespace): # copy intended:
            self.dict = dict(stack.dict)
            self.parent = None # copying search path could be dangerous
            self.stack = None # stack references screw up name searching.
        else:
            self.dict = kwdarg
            self.parent = parent # "reversed" linked list of execution namespaces
            self.stack = stack
    
    def bind(self, ns, name):
        if not isinstance(ns, Namespace):
            raise TypeError(str(ns) +" is not a namespace.")
        else:
            self.dict[name]=ns
            ns.parent = None # references do not point back, solves aliasing
            
    def unbind(self, name):
        if self.validate(name):
            del self.dict[name]
        # fail quiet on deletion that doesn't exist
        
    def get(self, name):
        if self.validate(name):
            return self.dict[name]
        else:
            raise AttributeError(name+" not found in "+str(self.dict.keys()))
            
    def validate(self, name):
        """Return whether id is a valid identifier for this namespace."""
        return name in self.dict
            
    def __str__(self):
        return "this: "+repr(self)+"\n"+\
               "stack: "+str(self.stack)+"\n"+\
               "Children: "+str(self.dict)+"\n"+\
               "parent: \n\\\n"+str(self.parent)+"\n/\n"
               
class Reference(Namespace):
    """Pointer equivalent in PSIL"""
    def __init__(self, seed):
        if isinstance(seed, str):
            self.string = seed
        elif isinstance(seed, Reference):
            self.string = seed.string[:] # force copy
        elif isinstance(seed, parse.Token):
            self.string = seed.string
        self.names = self.string.split(":")
        if self.names:
            self.first = self.names[0]
            self.last = self.names[-1]
        else:
            self.first = self.last = None
        
    def __iter__(self):
        return iter(self.names)
            
    def previous(self):
        """Returns a copy of the reference without this reference's last name.
        
        returns empty Reference if this Reference has a single name."""
        return Reference(":".join(self.names[:-2]))
        
    def __str__(self):
        return self.string
        
    def __repr__(self):
        return "PSIL Reference: "+self.string

class Literal(Namespace):
    """Superclass for all the literal types in PSIL."""
    def __init__(self):
        super().__init__()
    
class Code(Literal):
    """Type for a code literal."""
    def __init__(self, token=None):
        if isinstance(token, parse.Token):
            self.string = token.string
        elif isinstance(token, Code):
            self.string = token.string[:]
        else:
            self.string = "<Builtin>"
        super().__init__()
        
    def __iter__(self):
        if not hasattr(self, "op_list"):
            self.op_list = [op for op in parse.parse(iter(self.string))]
        return iter(self.op_list)
        
    def __repr__(self):
        return "PSIL Code Literal: "+str(self.string)
            
class LLCode(Code):
    """Superclass for any code not implemented in PSIL
    
    This code is invoked by calling the LLCode object during the Execute 
    instruction."""
    def __call__(self, state):
        """Hook for subclasses."""
        pass 
    
class String(Literal):
    """Type for a string literal.
    
    I may work on unicode support, but it's not required for a proof of 
    concept."""
    def __init__(self, token):
        """Creates the actual data object from the token representing it."""
        if isinstance(token, String):
            self.string = str(token.string)
        else:
            self.string = token.string
        super().__init__()
        
    def __repr__(self):
        return "\""+self.string+"\""
        
    def __str__(self):
        return self.string
        
class Numeric(Literal):
    """Type superclass for numbers in PSIL."""
    def __str__(self):
        return str(self.val)
    
class Integer(Numeric):
    """Type for integer data in PSIL."""
    def __init__(self, seed):
        if isinstance(seed, str):
            self.val = int(seed)
        elif isinstance(seed, Integer):
            self.val = int(seed.val)
        else:
            self.val = int(seed.string)
        super().__init__()
        
    def __repr__(self):
        return "PSIL Integer: "+str(self.val)
        
    def __mul__(self, other):
        if not isinstance(other, Numeric):
            raise TypeError("Cannot multiply non-Numeric "+str(other))
        if isinstance(other, Integer):
            return Integer(parse.Token(str(self.val*other.val)))
        elif isinstance(other, Float):
            return Float(parse.Token(str(self.val*other.val)))
        else:
            raise TypeError("Unrecognized Numeric "+str(other))
            
    def __sub__(self, other):
        if not isinstance(other, Numeric):
            raise TypeError("Cannot subtract non-Numeric "+str(other))
        if isinstance(other, Integer):
            return Integer(parse.Token(str(self.val-other.val)))
        elif isinstance(other, Float):
            return Float(parse.Token(str(self.val-other.val)))
        else:
            raise TypeError("Unrecognized Numeric "+str(other))
    
class Float(Numeric):
    """Type for integer data in PSIL."""
    def __init__(self, seed):
        if isinstance(seed, str):
            self.val = float(seed)
        elif isinstance(seed, Float):
            self.val = float(seed.val)
        else:
            self.val = float(seed.string)
        super().__init__()
        
    def __str__(self):
        return "PSIL Float: "+str(self.val)
    
class Stack:
    """Data stack that exists during execution of a PSIL program."""
    def __init__(self, size=None, stack=None):
        if size and stack:
            # initialize a shallow copy of a stack with a smaller size
            self.stack = stack
            self.size = size
        else:
            # new stack, original copy
            self.stack = []
            self.size = 0
    
    def append(self, data):
        if not isinstance(data, Namespace):
            raise TypeError("Cannot push, "+str(data)+" is not a Namespace!")
        else:
            self.stack.append(data)
            self.size += 1
    
    def pop(self):
        if self.size <= 0:
            raise IndexError("Tried to pop from empty stack")
        else:
            val = self.stack.pop()    
            self.size -= 1
        return val
        
    def peek(self):
        """Return the top item without removing it."""
        if self.size <= 0:
            raise IndexError("Tried to peek from empty stack")
        else:
            if isinstance(self.stack, Stack):
                return self.stack.peek()
            else:
                return self.stack[-1]

    def _str(self, size):
        if isinstance(self.stack, list):
            return str(self.stack[-size:])
        else:
            return self.stack._str(size)
            
    def __str__(self):
        return self._str(self.size)