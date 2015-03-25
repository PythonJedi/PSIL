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
    
    instructions = [parse.parse_file(file)] # stack of generators
    try:
        while instructions:
            ins_queue = instructions.pop()
            for ins in ins_queue:
                if isinstance(ins, parse.Execute):
                    instructions.append(ins_queue)
                    ins.run(env, instructions)     
                    break
                else:
                    ins.run(env) # everything else just modifies environment
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
    