#! /usr/bin/python3
"""Invocation for the PSIL interpreter.

Starts up the interpreter. Also handles file IO for programs."""

import sys

import data, parse

def main(file):
    """Run the interpreter using input from file.
    
    if file is stdin, interactive mode is used, handled by readline()."""
    
    # Global internal objects initialized here
    env = data.Namespace(None, data.Stack())
    
    instructions = [parse.parse(file)] # stack of generators
    try:
        while instructions and env:
            ins_queue = instructions.pop()
            for ins in ins_queue:
                if isinstance(ins, parse.Execute):
                    instructions.append(ins_queue)
                    code = env.stack.pop()
                    if hasattr(code, "name"): # executing code literal from namespace
                        pass # TODO: Helper function to insert the reference path into the search path.
                    else: # direct code literal execution
                        env = data.Namespace(env, data.Stack())
                    if not isinstance(code, data.Code):
                        raise TypeError("Tried to execute non-Code object "+str(code))
                    elif isinstance(code, data.LLCode):
                        code.run(env) # LLCode is a superclass of any code written in python
                    else:
                        instructions.append(code.instructions)
                    break
                    
                elif isinstance(ins, parse.External):
                    instructions.append(ins_queue)
                    instructions.append(parse.parse(open(ins.filename)))
                    break
                    
                elif isinstance(ins, parse.Push):
                    if isinstance(ins.value, Reference):
                        ins.value = env.search(ins.value)
                    env.stack(ins.value)
            env = env.parent
            while env and not env.stack:
                env = env.parent
                    
    except e:
        print(str(e))
    
def readline(file):
    """Read a line from the file.
    
    This is mostly to abstract out interactive vs. file based input."""
    if file == sys.stdin: # interactive mode!
        sys.stdout.write("| | ")
        return sys.stdin.readline().rstrip("\\\n")
    else:
        return file.readline(100).rstrip("\\\n"
    
if __name__ == "__main__":
    if len(sys.argv) > 1: # sys.argv[0] is the script name
        try:
            f = open(sys.argv[1], "r")
            main(f)
        finally:
            f.close()
    else:
        print("Need to implement an interacitve mode!")
    