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
    
    line = readline(file)
    instructions = []
    try:
        while line
            line, instructions = parse.parse(line) # parse returns unfinished characters
            for ins in instructions:
                ins.run(env)
            line += readline(file)
    except e:
        print(str(e))
    
def readline(file):
    """Read a line from the file.
    
    This is mostly to abstract out interactive vs. file based input."""
    if file == sys.stdin: # interactive mode!
        sys.stdout.write("| | ")
        sys.stdin.readline()
    else:
        return file.readline(100) # lines shouldn't be longer than 80, gives some slack
    
if __name__ == "__main__":
    if len(sys.argv) > 1: # sys.argv[0] is the script name
        try:
            f = open(sys.argv[1], "r")
            main(f)
        finally:
            f.close()
    else:
        main(sys.stdin)
    