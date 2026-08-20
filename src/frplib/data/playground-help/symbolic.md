# Symbolic Manipulation

ATTN:Discussion


## Functions for Working with Symbols

+ `is_symbolic(x)` :: returns true if `x` is a symbolic expression

+ `gen_symbol()` :: returns a unique symbol name every time it is called

+ `symbols(names)` takes a string of space-separated names and returns a tuple
      of tuples with those names. Supports automatically numbered symbols with
      a `...` pattern.

+ `symbol(name)` takes a string and creates a symbolic term with that name

+ `substitute(quantity, mapping)` :: substitutes values from mapping for the
      symbols in `quantity`; mapping is a dictionary associating symbol names with values.
      Not all symbols need to be substituted; if all are substituted with a numeric value
      then the result is numeric.

+ `substitute_with(mapping)` :: returns a function that takes a quantity and substitutes
      with mapping in that quantity.

+ `substitution(quantity, **kw)` :: like `substitute` but takes names and values as
      keyword arguments rather than through a dictionary.

