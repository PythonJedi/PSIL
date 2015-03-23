#! /usr/bin/python3
"""An outline of PSIL's type system.

Author: Timothy Hewitt
Date: 2015-03-19"""

class Namespace:
    """Represents the type of a namespace, the catchall type."""

class Literal(Namespace):
    """Superclass for all the literal types in PSIL."""
    
class Code(Literal):
    """Type for a code literal."""
    
class String(Literal):
    """Type for a string literal.
    
    I may work on unicode support, but it's not required for a proof of 
    concept."""
    
class Numeric(Literal):
    """Type superclass for numbers in PSIL."""
    
class Integer(Numeric):
    """Type for integer data in PSIL."""
    
class Float(Numeric):
    """Type for integer data in PSIL."""