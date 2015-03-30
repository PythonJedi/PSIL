#! /usr/bin/python3
"""Invocation for the PSIL interpreter.

Starts up the interpreter. Also handles file IO for programs."""

import sys

import data, parse

class Interpreter:
    def __init__(self, file):
        self.char_stream = file
        self.env = data.Namespace(None, data.Stack())
        self.instructions = [parse.parse(file)] 
        self.op_stream = None
        
    def run(self):
        """Run the interpreter
        
        if file is stdin, interactive mode should be used."""
        try:
            while self.instructions and self.env:
                self.op_stream = self.instructions.pop()
                for ins in self.op_stream:
                    self.op(ins)
                self.env = self.env.parent
                while self.env and not self.env.stack:
                    self.env = self.env.parent
                        
        except e:
            print(str(e))
            
    def op(self, ins):
        """Execute a single instruction."""
        if isinstance(ins, parse.Execute):
            instructions.append(op_stream)
            code = self.env.stack.pop()
            if hasattr(code, "name"): # executing code literal from namespace
                self.build_search_path(code.name)
            else: # direct code literal execution
                self.env = data.Namespace(self.env, data.Stack())
            
            if not isinstance(code, data.Code):
                raise TypeError("Tried to execute non-Code object "+str(code))
            elif isinstance(code, data.LLCode):
                code.run(self) # LLCode is a superclass of any code written in python
            else:
                self.instructions.append(code.instructions())
            return True
            
        elif isinstance(ins, parse.External):
            instructions.append(ins_queue)
            instructions.append(parse.parse(open(ins.filename)))
            return True
            
        elif isinstance(ins, parse.Push):
            if isinstance(ins.value, parse.Reference):
                ins.value = self.env.deref(ins.value) # dereference
            self.env.stack.push(ins.value)
            return False
            
    def build_search_path(self, name):
        """Appends the namespaces in name to the search path. 
        
        should only be called with a verified name."""
        
    
    
if __name__ == "__main__":
    if len(sys.argv) > 1: # sys.argv[0] is the script name
        try:
            f = open(sys.argv[1], "r")
            main(f)
        finally:
            f.close()
    else:
        print("Need to implement an interacitve mode!")
    