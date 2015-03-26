## PSIL Seriously Isn’t Lisp

#### *Timothy Hewitt*

### Purpose

The primary purpose of PSIL is to be a self-guided exercise in language design and implementation. Over the evolution of the project from a simple joke on Lisp it has acquired an unconventional syntax and execution model that make it worth implementing and analyzing.

### History

PSIL started in the late spring of 2014 as a loose definition to make fun of Lisp. As such, excessive use of parenthesis and postfix notation were required. 

Research for an unrelated project uncovered that postfix notation minimizes syntactic analysis, spurring on development of a formal syntax definition and a general description of the execution process. 

Current development is focusing on writing a fully featured interpreter and filling out minor details that make PSIL a much more usable language.

Future directions include creating a statically compiled variant with strong typing. This could let the language become self-implementing.

### Syntax

PSIL’s syntax is extremely simple to describe since most functionality is left to the standard library built-in functions.

Any PSIL program is encapsulated inside an expression that is delimited by parenthesis and contains whitespace separated sub-expressions, literal values, or named references. The parenthesis allow the interpreter to keep track of how many values a code literal is allowed to pull off the stack. 

PSIL’s concept of a code literal is similar to Python’s function object or C’s function pointer. It is a section of PSIL code that can be placed on the stack, assigned to a name, and executed at will. Code literals are delimited by matching curly braces and can be nested.

### Execution Model

PSIL uses an explicitly stack-based execution model, all literals and references in the source code are pushed to the stack before the end of an expression triggers the pop and execution of a code literal.

However, PSIL also has to handle named variables and complex datatypes. It does so by keeping a directed graph of namespaces. Each namespace has a mapping of names to a reference of the corresponding sub-namespace. Some namespaces also have a reference to the next namespace to begin a name search.

When a name is dereferenced, a depth-first search is initiated following this chain until the first identifier in the name is found. If the name is not found, an exception is raised. Once the first identifier is found, the search follows the names in the mappings until an identifier is not found or the entire name is dereferenced.

Searching in a graph until a null pointer is found can cause infinite loops. This is guaranteed to not happen because the “parent” reference cannot be directly manipulated from inside the language and the root namespace always points to null. Dereferencing the name will eventually consume the whole name, guarding against infinite loops in the second phase of the search.

### License

This project is released under the zlib license. See [LICENSE.txt]()

