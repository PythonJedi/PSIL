"""Lexical analyzer and parser for the PSIL Interpreter.

Part of Timothy Hewitt's UTD REx 2015 project.
Author: Timothy Hewitt
Date: 2105-03-20"""

import re

import data

## The purpose of a lexer and parser is to turn the source code into a series of
## commands for either a compiler or interpreter virtual machine.

## I'm going to use a highly object oriented approach to this problem. This
## approach uses two levels of abstraction between the incoming source strings
## and the virtual machine. The first layer are the Token and Literal objects.
## These turn source strings into abstract concepts of the syntax. As this is a
## stack-based postfix language, the syntax is nearly one-to-one with the 
## lexical abstraction. The second layer are the Instruction classes, which get 
## sent back to the virtual machine's execution queue. The purpose of the 
## Instruction classes is to implement the builtin functions more than anything 
## else.

def load(file):
    string = ""
    for line in file:
        string += line.rstrip("\n") # backslashes need to be handled carefully
    return string

class Token:
    """Superclass for lexical elements of the language.
    
    Any discrete element of the language will have an abstraction that 
    subclasses this one."""
    def __init__(self, string):
        self.string = string
        
    def evaluate(self):
        """Turns Token into an Instruction."""
        pass

class Reference(Token):
    """A reference to some namespace in the namespace tree.
    
    May or may not be valid, Token objects just translate from strings to 
    abstractions."""
    regex = re.compile(r"""[a-zA-Z0-9_] +   # first reference
                           (?:              # group start
                           :[a-zA-Z0-9_] +  # following reference
                           ) *              # match any and all following
                           """, re.X)
    def __init__(self, string):
        self.names = string.split(":")
        
    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError("References can only be indexed by integers!")
        else:
            return self.names[index]
    def next(self):
        """Move to the next name.
        
        returns self after popping the first item in self.names"""
        self.names.pop(0)
        return self
        
    def copy(self):
        return Reference(str(self)) # stupid, yes, but it works
    
    def __str__(self):
        return ":".join(self.names)
        
class BeginExpression(Token):
    """Not sure if I need this, here just in case."""
    regex = re.compile(r'\({1}') # seriously, it's just an open parenthesis
    
class EndExpression(Token):
    """Triggers the creation of an Execute Instruction."""
    regex = re.compile(r'\){1}') # just an end parentheses

class Literal(Token):
    """Superclass for Numeric, Text, and Code Literals."""
    
class String(Literal):
    """Token for a string literal."""
    regex = re.compile(r'"\.*"') # need to remove backslash-newline-whitespace sequences 
    
class Code(Literal):
    """Token for code literals."""
    regex = re.compile(r'\{\.\}') # really, lexing of the internals happens later
    
class Numeric(Literal):
    """Superclass for Numeric literals."""
    
class Integer(Numeric):
    """Token for Integer literals."""
    regex = re.compile(r'[1-9][0-9]*') # other bases may be supported in the future
    
class Float(Numeric):
    """Token for floating point literals."""
    regex = re.compile(r'''[0-9]* # beginning integer component
                           \.     # decimal point
                           [0-9]* # fractional component ''', re.X)
        
## Begin instruction classes

class Instruction:
    """A single instruction for the PSIL virtual machine."""
    
class Push(Instruction):
    """Push a literal on the stack."""
    def __init__(self, value):
        self.value=value
        
    def run(self, env):
        env.stack.push(self.value)

class Execute(Instruction):
    """Execute a code literal off the top of the stack."""
    def __init__(self, size):
        self.size = size
    
    def run(self, env):
        code = env.stack.pop()
        if not isinstance(code, data.Code):
            raise TypeError("Tried to execute non-Code object "+str(code))
        else:
            n = code.name.copy()
            for name in n.names:
                env = data.Namespace(env) # build the search stack
            code.run(env)
    
class Bind(Instruction):
    """Pull a value and a name off the stack and bind them in the namespace."""
    def __init__(self, name):
        self.name = name
        
    def run(self, env):
        env.bind(env.stack.pop(), self.name)
    
class Math(Instruction):
    """Superclass for the math functions."""
    
class Dereference(Instruction):
    """Search the namespace tree for a certain namespace and push it.
    
    Searches up from the current execution environment through the parent 
    reference and then back down through named references in the environment's 
    dictionary items."""
    def __init__(self, name):
        self.name = name
    
    def run(self, env):
        stack = env.stack
        while env and not self.name[0] in env.dict:
            env = env.parent
        if env:
           d = self.follow(self.name.copy(), env)
           d.name = self.name
           stack.push(d)
        else:
            raise AttributeError(str(self.name)+" not found in namespace tree.")
    
    def follow(self, name, env):
        if not name: # name empty, env is target
            return env
        elif name[0] in env.dict:
            return self.follow(name.next(), env.dict[name[0]])
        else:
            raise AttributeError("Search for "+str(self.name)+" failed at "+\
                                  str(name[0])+" in "+str(env))

