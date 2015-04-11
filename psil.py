#! /usr/bin/python3
"""Invocation for the PSIL interpreter.

Starts up the interpreter. Also handles file IO for programs."""

import sys

import data, parse, stdlib

class Interpreter:
    def __init__(self, file):
        self.char_stream = parse.chars(file)
        self.env = data.Namespace(data.Stack(), None, **stdlib.builtins)
        self.op_stream_stack = [parse.parse(self.char_stream)] 
        self.arg_len_stack = []
        
    def run(self):
        """Run the interpreter
        
        if file is stdin, interactive mode should be used."""
        try:
            for op in self:
                #print(op)
                if isinstance(op, parse.Push):
                    self.env.stack.append(op.value)
                    self.arg_len_stack[-1] += 1
                    
                elif isinstance(op, parse.NewExpression):
                    self.arg_len_stack.append(0)
                    
                elif isinstance(op, parse.Execute):
                    value = self.env.stack.pop()
                    self.arg_len_stack[-1] -= 1
                    
                    if isinstance(value, data.Code):
                        self.append_env()
                        self.push(iter(value))
                    
                    elif isinstance(value, data.Reference):
                        code = self.search(value)
                        assert isinstance(code, data.Code)
                    
                        if isinstance(code, data.LLCode):
                            code(self)
                            self.arg_len_stack.pop()
                        
                        else:
                            self.append_env(value)
                            self.push(iter(code))
                #print(self.arg_len_stack)
                        
        except Exception as e:
            #print(self.env.stack)
            raise e # need the stack trace for debugging!
            
    def append_env(self, reference=None):
        """Appends a new environment.
        
        If a reference is given the new environment is appended below the 
        namespace pointed to by that reference, with the search path pointing up
        through the reference."""
        stack = self.env.stack # Need to get reference before traversing
        if reference: # set search path
            start = self.search_up(reference)
            for name in reference:
                if start.validate(name):
                    start = start.get(name)
                    start.parent = self.env
                else:
                    raise AttributeError("Failed to find "+str(name))
                self.env = start
        
        # make new namespace
        self.env = data.Namespace(data.Stack(self.arg_len_stack.pop(),
                                             stack),
                                 self.env)
        
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
        
    def search(self, reference):
        if reference.last: # verifies reference is not empty
            return self.search_down(reference, self.search_up(reference))
        else:
            return self.env
        
    def search_up(self, reference):
        ns = self.env
        while ns and not ns.validate(reference.first):
            ns = ns.parent
        if ns == None:
            raise NameError(str(reference)+" not found.")
        else:
            return ns
    
    def search_down(self, reference, namespace):
        for name in reference:
            if namespace.validate(name):
                namespace = namespace.get(name)
            else:
                raise AttributeError(name+" not found in "+str(namespace))
        return namespace
        
    def push(self, code):
        self.op_stream_stack.append(iter(code))
        
    def __iter__(self):
        return self
        
    def __next__(self):
        op = None
        while not op and self.op_stream_stack:
            try:
                op = self.op_stream_stack[-1].__next__() # just need one
            except StopIteration:
                self.op_stream_stack.pop()
                if self.arg_len_stack:
                    self.arg_len_stack[-1] += self.env.stack.size
                self.pop_env()
        if op:
            return op
        else: # op_stream_stack is empty
            raise StopIteration()
    
    
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
    