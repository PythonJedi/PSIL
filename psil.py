#! /usr/bin/python3
"""Invocation for the PSIL interpreter.

Starts up the interpreter. Also handles file IO for programs."""

import sys

import data, parse, stdlib

class Interpreter:
    def __init__(self, file):
        self.char_stream = parse.chars(file)
        self.env = data.Namespace(None, data.Stack(), stdlib.builtins**)
        self.op_stream_stack = [parse.parse(self.char_stream)] 
        self.arg_len_stack = []
        
    def run(self):
        """Run the interpreter
        
        if file is stdin, interactive mode should be used."""
        try:
            for op in self:
                if isinstance(op, parse.Push):
                    self.env.stack.push(op.value)
                    
                elif isinstance(op, parse.NewExpression):
                    self.arg_len_stack.append(0)
                    
                elif isinstance(op, parse.Execute):
                    value = self.env.stack.pop()
                    
                    if isinstance(value, data.Code):
                        self.append_env()
                        self.push(iter(value))
                    
                    elif isinstance(value, data.Reference):
                        code = self.search(value)
                        assert isinstance(code, data.Code)
                    
                        if isinstance(code, data.LLCode):
                            code(self)
                        
                        else:
                            self.append_env(value)
                            self.push(iter(code))
                        
        except Exception as e:
            #print(self.env.stack)
            raise e # need the stack trace for debugging!
            
    def append_env(self, reference=None):
        """Appends a new environment.
        
        If a reference is given the new environment is appended below the 
        namespace pointed to by that reference, with the search path pointing up
        through the reference."""
        if reference: # set search path
            start = self.search_up(reference)
            for name in reference:
                if start.validate(name):
                    start = start.get(name)
                    start.parent = self.env
                else:
                    raise AttributeError("Failed to find "+str(name))
                self.env = start
        
        # Add new namespace
        self.env = data.Namespace(self.env,
                                  data.Stack(self.arg_len_stack.pop(),
                                             self.env.stack)
                                 )
                
    def pop_env(self):
        """Moves the environment back to the previous execution namespace.
        
        first moves the current env reference up the search path and then
        continues up until it finds an executable environment (one with a stack 
        reference)."""
        self.env = self.env.parent
        while self.env and not self.env.stack:
            temp = self.env
            self.env = self.env.parent
            temp.parent = None
        
    def search(self, name):
        if not name.string: # empty ref
            return self
        nm = name.copy()
        start = self.search_up(name)
        val = start.search_down(name)
        val.name = nm # need unmodified copy
        return val
    
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
    
    
if __name__ == "__main__":
    if len(sys.argv) > 1: # sys.argv[0] is the script name
        try:
            f = open(sys.argv[1], "r")
            interpreter = Interpreter(f)
            interpreter.run()
        finally:
            f.close()
    else:
        print("Need to implement an interactive mode!")
    