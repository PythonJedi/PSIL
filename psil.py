#! /usr/bin/python3
"""Invocation for the PSIL interpreter.

Starts up the interpreter. Also handles file IO for programs."""

import sys

import data

def main(file):
    """Run the interpreter using input from file.
    
    if file is stdin, interactive mode is used, handled by readline()."""
    
    # Global internal objects initialized here
    env = data.Namespace()
    env.bind(data.Stack(), "__stack__")
    
    # Interpreter loop
        # input chunk, append to previous amount
        # parse chunk, remainder returned
        # execute parsed data
    
    # Finalization, close user opened files
    
def readline(file):
    """Read a line from the file.
    
    This is mostly to abstract out between interactive and file based input."""
    if file == sys.stdin: # interactive mode!
        # do interactive mode stuff
    else:
        # actual file, read a line
    
if __name__ == "__main__":
    if len(sys.argv) > 1: # sys.argv[0] is the script name
        try:
            f = open(sys.argv[1], "r")
            main(f)
        finally:
            close(f)
    else:
        main(sys.stdin)
    