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
    
    def bind(self, ns, id):
        if not isinstance(ns, Namespace):
            raise TypeError(str(ns) +" is not a namespace.")
        else:
            self.dict[id]=ns
            ns.parent = None # references do not point back, solves aliasing
            #print("Bound "+str(ns)+" to "+id+" in "+str(self))
            
    def unbind(self, id):
        if self.validate(id):
            del self.dict[id]
        # fail quiet on deletion that doesn't exist
        
    def grab(self, id):
        if self.validate(id):
            return self.dict[id]
    
    def deref(self, name):
        if not name.string: # empty ref
            return self
        nm = name.copy()
        start = self.search_up(name)
        val = start.search_down(name)
        val.name = nm # need unmodified copy
        return val
        
    def validate(self, id):
        """Return whether id is a valid identifier for this namespace."""
        return id in self.dict
    
    def search_up(self, name):
        if self.validate(name[0]):
            return self
        elif self.parent: # name not found, but not root namespace
            return self.parent.search_up(name) # Namespace.search_up(self.parent, name)
        else: # root namespace, name not found
            raise AttributeError(str(name)+" not found in namespace tree.")

    def search_down(self, name):
        if not name.names:
            return self # finished search successfully
        elif self.validate(name[0]):
            return self.dict[name[0]].search_down(name.next())
        else:
            raise AttributeError(str(name)+" not found in namespace tree.")
            
    def __str__(self):
        return "this: "+repr(self)+"\n"+\
               "stack: "+str(self.stack)+"\n"+\
               "Children: "+str(self.dict)+"\n"+\
               "parent: \n\\\n"+str(self.parent)+"\n/\n"
               
class Reference(Namespace):
    """Pointer equivalent in PSIL"""
    def __init__

class Literal(Namespace):
    """Superclass for all the literal types in PSIL."""
    def __init__(self):
        super().__init__()
    
class Code(Literal):
    """Type for a code literal."""
    def __init__(self, token=None):
        if token:
            self.string = token.string
        else:
            self.string = "<Builtin>"
        super().__init__()
        
    def instructions(self):
        if not hasattr(self, "op_list"):
            self.op_list = [op for op in parse.parse(iter(self.string))]
        return iter(self.op_list)
        
    def __str__(self):
        return "PSIL Code Literal: "+str(self.string)
            
class LLCode(Code):
    """Superclass for any code not implemented in PSIL
    
    This code is invoked by calling code.run(env) in the Execute instruction."""
    
class String(Literal):
    """Type for a string literal.
    
    I may work on unicode support, but it's not required for a proof of 
    concept."""
    def __init__(self, token):
        """Creates the actual data object from the token representing it."""
        self.string = token.string
        super().__init__()
        
    def __str__(self):
        return "PSIL String: "+self.string
        
class Numeric(Literal):
    """Type superclass for numbers in PSIL."""
    
class Integer(Numeric):
    """Type for integer data in PSIL."""
    def __init__(self, token):
        self.val = int(token.string)
        super().__init__()
        
    def __str__(self):
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
    def __init__(self, token):
        self.val = float(token.string)
        super().__init__()
        
    def __str__(self):
        return "PSIL Float: "+str(self.val)
    
class Stack:
    """Data stack that exists during execution of a PSIL program."""
    def __init__(self, size=None, stack=None):
        if size and stack: 
            # initialize a shallow copy of a stack with a smaller size
            self.list = stack.list
            self.size = size
        else:
            # new stack, original copy
            self.list = []
            self.size = 0
        print("Created Stack with size: "+str(self.size)+"\nCan access: "+str(self.list[-self.size:]))
    
    def push(self, data):
        if not isinstance(data, Namespace):
            raise TypeError("Cannot push, "+str(data)+" is not a Namespace!")
        else:
            self.list.append(data)
            self.size += 1
    
    def pop(self):
        if self.size <= 0:
            raise IndexError("Tried to pop from empty stack")
        else:
            self.size -= 1
    
        return self.list.pop()
        
    def peek(self):
        """Return the top item without removing it."""
        if self.size <= 0:
            raise IndexError("Tried to peek from empty stack")
        return self.list[-1]

    def __str__(self):
        return str(self.list[-self.size:])