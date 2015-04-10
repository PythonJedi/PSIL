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
("foo" bar {(baz:bar -4 add)} "quux" spam)
(eggs (ham (toast (bacon fork))))
# Can you tell I'm hungry? #
(((cheese grill) pizza) 0.45)
""" # Not a comprehensive test, but should find most issues

def preprocess(char_stream):
    """Preprocess the inbound character stream.
    
    This removes comments and spaces out tokens."""
    for c in char_stream:
        if c == "#":
            Comment.munch(char_stream)
            continue # no need to pass comments on to tokenizer
        elif c in ")}":
            yield " "
        elif c in "({":
            yield c 
            c = " "
        elif c == "\n":
            continue # newlines mean nothing
        yield c # this means that the ')' and '}' are passed back 

def tokenize(char_stream):
    """tokenize the character stream.
    
    Tried to use regular expressions to do this, but tokenizing a context free 
    language is impossible with a regex tokenizer."""
    
    preproc = preprocess(char_stream)
    for c in preproc:
        if c in " \t\n": # Whitespace not inside a string literal
            continue # run to the next iteration
        elif c == "(": # start new expression
            yield StartExpression(c)
        elif c == ")": # finish expression
            yield EndExpression(c)
        elif c == "{":
            yield Code.munch(preproc) # eats end curly brace
        else: # Reference, numeric literal, string, or error
            if c == "\"": # Beginning of string literal
                yield String.munch(preproc) # eats end quote
            elif c.isdigit() or c in ".-+": # numeric literal
                yield Numeric.munch(c, preproc) # c is the first character
            else: # Reference or syntax error
                yield Reference.munch(c, preproc) # c is the first character
                
def parse(char_stream):
    """Parse an incoming character stream.
    
    generates a stream of Instruction objects."""
    tokens = tokenize(char_stream)
    for t in tokens:
        yield t.evaluate()
        
def chars(file):
    """turns a file like object into a character stream"""
    for line in file:
        for c in line:
            yield c
                
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
        raise SyntaxError("Unclosed comment in parsed code!")

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
    
    def evaluate(self):
        return Push(data.Reference(self))
        
    def __str__(self):
        return "PSIL Reference Token: "+self.string
        
class StartExpression(Token):
    """Delineates the start of an expression.
    
    Turns into a NewExpression instruction."""
    def evaluate(self):
        return NewExpression(self)
    
class EndExpression(Token):
    """Triggers the creation of an Execute Instruction."""
    def evaluate(self):
        return Execute(self)
        
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
        return "PSIL String Token: "+self.string
        
    def evaluate(self):
        return Push(data.String(self))
    
    
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
        
    def evaluate(self):
        return Push(data.Code(self))
        
    def __str__(self):
        return "PSIL Code Literal Token: "+self.string
    
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
    
    def evaluate(self):
        return Push(data.Integer(self))
    
    def __str__(self):
        return "PSIL Integer Token: "+self.string
        
class Float(Numeric):
    """Token for floating point literals."""
    def evaluate(self):
        return Push(data.Float(self))
    
    def __str__(self):
        return "PSIL Float Token: "+self.string

#========================== #
# Begin instruction classes #
#========================== #

class Instruction:
    """A single instruction for the PSIL virtual machine.
    
    These are the actions that the interpreter needs to take to let the language
    take care of the rest of itself. NewExpression isn't explicitly needed, but 
    makes runtime errors easier to trace."""
    def __init__(self, token):
        pass # Don't need to do anything with the token
    
    
class Push(Instruction):
    """Push a literal on the stack."""
    def __init__(self, obj):
        self.value=obj
        
    def __str__(self):
        return "PUSH "+str(self.value)
        
class NewExpression(Instruction):
    """Trigger for creation of a new expression.
    
    Allows the interpreter to keep track of the "parameters" for a given 
    expression."""
    def __str__(self):
        return "NEW EXPRESSION"

class Execute(Instruction):
    """Execute a code literal off the top of the stack."""
    def __str__(self):
        return "EXECUTE"

if __name__ == "__main__":
    for i in parse(iter(TOKENTEST)):
        print(i)