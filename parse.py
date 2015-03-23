"""Lexical analyzer and parser for the PSIL Interpreter.

Part of Timothy Hewitt's UTD REx 2015 project.
Author: Timothy Hewitt
Date: 2105-03-20"""

import data

## The purpose of a lexer and parser is to turn the source code into a series of
## commands for either a compiler or interpreter virtual machine.

## I'm going to use a highly object oriented approach to this problem.

class Instruction:
    """A single instruction for the PSIL virtual machine."""
    
class Push(Instruction):
    """Push a value on the stack."""
    def __init__(self, value):
        self.value=value

class Exec(Instruction):
    """Execute a code literal off the top of the stack."""
    
class Bind(Instruction):
    """Pull a value and a name off the stack and bind them in the namespace."""
    
class Math(Instruction):
    """Superclass for the math functions."""
    
class 