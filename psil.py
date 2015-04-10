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
                    if isinstance(value, data.LLCode):
                        value(self)
                    elif isinstance(value, data.Code):
                        self.append_env()
                        self.push(iter(value))
                    elif isinstance(value, data.Reference):
                        
        except Exception as e:
            #print(self.env.stack)
            raise e # need the stack trace for debugging!
            
    def op(self, ins):
        """Execute a single instruction."""
        if isinstance(ins, parse.Execute):
            self.op_stream_stack.append(self.op_stream)
            code = self.env.stack.pop()
            
            if not isinstance(code, data.Code):
                raise TypeError("Tried to execute non-Code object "+str(code))
            elif isinstance(code, data.LLCode):
                print(code)
                print(self.env.stack)
                print(self.arg_len_stack)
                code.run(self) # LLCode is a superclass of any code written in python
            else:
                if hasattr(code, "name"): # executing named code literal
                    self.build_search_path(code.name)
                    print(code.name)
                else:
                    print("Anonymous")
                print(self.env.stack)
                print(self.arg_len_stack)
                self.append_env(data.Namespace(self.env, data.Stack(self.arg_len_stack.pop()-1, self.env.stack)))
                
                self.op_stream_stack.append(code.instructions())
                return True
            
        elif isinstance(ins, parse.Push):
            if isinstance(ins.value, parse.Reference):
                ins.value = self.env.deref(ins.value) # dereference
            self.env.stack.push(ins.value)
            if self.arg_len_stack:
                self.arg_len_stack[-1] += 1
            else:
                self.arg_len_stack.append(1) # starting out
        return False
            
    def build_search_path(self, name):
        """Appends the namespaces in name to the search path. 
        
        should only be called with a verified name."""
        trav = self.env.search_up(name)
        name = name.next() # need to move to the next name as the first was found
        
        while name.names:
            if trav.validate(name[0]):
                self.append_env(trav.grab(name[0]))
            else:
                raise AttributeError("Failed to find "+str(name))
            trav = self.env
                
    def clean_search_path(self):
        """Moves the environment back to the previous execution namespace.
        
        first moves the current env reference up the search path and then
        continues up until it finds an executable environment (one with a stack 
        reference)."""
        self.env = self.env.parent
        while self.env and not self.env.stack:
            self.env = self.env.parent
                
    def append_env(self, env):
        assert not self.env == env
        env.parent = self.env
        self.env = env
        
    def deref(self, name):
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
    