"""Lexical analyzer and parser for the PSIL Interpreter.

Part of Timothy Hewitt's UTD REx 2015 project.
Author: Timothy Hewitt
Date: 2105-03-20"""

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

TOKENTEST = """
(foo bar (baz:bar -4 add) "quux" spam)
(eggs (ham (toast (bacon fork))))
# Can you tell I'm hungry? #
(((cheese grill) pizza) 0.45)
""" # Not a comprehensive test, but should find most issues

def load(file):
    string = ""
    for line in file:
        string += line
    return string

def tokenize(string):
    """tokenize the string, yielding Token objects.
    
    Tried to use regular expressions to do this, but tokenizing a context free 
    language is impossible with a regex tokenizer."""
    
    # need to insert spaces before close parenthesis
    string = " )".join(string.split(")"))
    
    iterator = iter(string) # need to be able to pass to subsidiary functions
    expr_size = []  #stack to keep track of the size of the current expression
    for c in iterator:
        if c in " \t\n": # Whitespace not inside a string literal
            continue # run to the next iteration
        elif c == "(": # start new expression
            if expr_size: # empty expression size stack means root expression
                expr_size.append(expr_size.pop()+1) # expression counts as element in encapsulating expression
            expr_size.append(0) # make a new entry in the expression tracker
            
        elif c == ")": # finish expression
            yield Expression(expr_size.pop()-1)
            # need to subtract one because the code literal that is executed shouldn't count
        elif c == "{":
            if expr_size:
                expr_size.append(expr_size.pop()+1)
            else:
                raise SyntaxError("Code literal outside expression!")
            yield Code.munch(iterator) # eats end curly brace
        elif c == "#":
            Comment.munch(iterator)
            continue 
        else: # Reference, numeric literal, string, or error
            if c == "\"": # Beginning of string literal
                if expr_size:
                    expr_size.append(expr_size.pop()+1)
                else:
                    raise SyntaxError("String literal outside expression!")
                yield String.munch(iterator) # eats end quote
            elif c.isdigit() or c in ".-": # numeric literal
                if expr_size:
                    expr_size.append(expr_size.pop()+1)
                else:
                    raise SyntaxError("Numeric literal outside expression!")
                yield Numeric.munch(c, iterator) # c is the first character
            else: # Reference or syntax error
                if expr_size:
                    expr_size.append(expr_size.pop()+1)
                else:
                    raise SyntaxError("String literal outside expression!")
                yield Reference.munch(c, iterator) # c is the first character
            
class Token:
    """Superclass for lexical elements of the language.
    
    Any discrete element of the language will have an abstraction that 
    subclasses this one."""
    def __init__(self, string):
        self.string = string
        
    def evaluate(self):
        """Turns Token into an Instruction."""
        pass
        
class Comment(Token):
    """Never need to instance, just nice to have."""
    def munch(iter):
        for c in iter:
            if c == "#":
                return # comments mean nothing, just need to push the iterator over them
        raise SyntaxError("Unclosed comment in parsed string!")

class Reference(Token):
    """A reference to some namespace in the namespace tree.
    
    May or may not be valid, Token objects just translate from strings to 
    abstractions."""
    def munch(c, iter):
        chars = [c]
        for c in iter:
            if c in " \n\t":
                break
            if c == ":" or c.isalpha():
                chars.append(c)
            else:
                raise SyntaxError("Invalid character in reference: "+c)
        return Reference("".join(chars))
        
    def __init__(self, string):
        self.string = string
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
        return Reference(repr(self)) # stupid, yes, but it works
    
    def __repr__(self):
        return ":".join(self.names)
        
    def __str__(self):
        return "PSIL Reference: "+self.string
    
class Expression(Token):
    """Triggers the creation of an Execute Instruction."""
    def __init__(self, size):
        self.size = size
    
    def evaluate(self):
        return Execute(self.size)
        
    def __str__(self):
        return "PSIL Expression, size: "+str(self.size)

class Literal(Token):
    """Superclass for Numeric, Text, and Code Literals."""
    
class String(Literal):
    """Token for a string literal."""
    def munch(iter):
        chars = []
        escape = False
        for c in iter:
            if escape:
                chars.append(c)
            elif c == "\\":
                escape = True
            elif c == "\"":
                return String("".join(chars))
            else:
                chars.append(c)
        raise SyntaxError("Reached end of source string parsing string literal")
        
    def __init__(self, string):
        self.string = string
        
    def __str__(self):
        return "PSIL String: "+self.string
        
    def evaluate(self):
        return Push(data.String(self.string))
    
    
class Code(Literal):
    """Token for code literals."""
    def munch(iter):
        chars = []
        lev = 1
        for c in iter:
            if c == "{":
                lev += 1
            elif c == "}":
                if lev == 1: # match for starting brace!
                    return Code("".join(chars))
                lev -= 1
            chars.append(c) # always add the character to the literal
            
    def __init__(self, string):
        self.string = string
    def __str__(self):
        return "PSIL Code Literal: "+self.string
    def evaluate(self):
        """Needs some work, as code literals expand to many tokens"""
        return Push(data.Code(self.string))
    
class Numeric(Literal):
    """Superclass for Numeric literals."""
    def munch(c, iter):
        chars = [c] # c is the character eaten by the tokenizer
        float = False
        for c in iter:
            if c in " \n\t":
                break
            if c == ".":
                if not float:
                    float = True
                else:
                    raise SyntaxError("Invalid numeric literal: Too many '.'")
            elif not c.isdigit():
                raise SyntaxError("Non-Digit in Numeric Literal")
            chars.append(c)
        if float:
            return Float("".join(chars))
        else:
            return Integer("".join(chars))
    
class Integer(Numeric):
    """Token for Integer literals."""
    def __init__(self, string):
        self.string = string
    def __str__(self):
        return "PSIL Integer: "+self.string
        
class Float(Numeric):
    """Token for floating point literals."""
    def __init__(self, string):
        self.string = string
    def __str__(self):
        return "PSIL Float: "+self.string
    
## Begin instruction classes

class Instruction:
    """A single instruction for the PSIL virtual machine.
    
    These are the implied actions: push, dereference, and execute. All other actions in the language are invoked like any other """
    
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
    
    def run(self, env, instructions):
        code = env.stack.pop()
        if not isinstance(code, data.Code):
            raise TypeError("Tried to execute non-Code object "+str(code))
        elif isinstance(code, data.LLCode):
            code.run(env) # LLCode is a superclass of any code written in python
        else:
            instructions.append(code.instructions)
    
class Dereference(Instruction):
    """Search the namespace tree for a certain namespace and push it.
    
    Searches up from the current execution environment through the parent 
    reference and then back down through named references in the environment's 
    dictionary items."""
    def __init__(self, name):
        self.name = name
        
    def string(s, env):
        """Dereference the string s given environment env."""
    
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

if __name__ == "__main__":
    for t in tokenize(TOKENTEST):
        print(t)