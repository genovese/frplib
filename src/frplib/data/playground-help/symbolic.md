# Symbolic Manipulation

`frplib` has the ability to represent, manipulate, and simplify
symbolic quantitiess and expressions.
The capabilities are somewhat limited at the moment, but improving.
For simple expressions, they do well, but for long iterative computations,
the symbolic expressions can get complicated.

Symbolic expressions are quantities and can be used for the values
and weights of a Kind and for the values of an FRP. Note that we
cannot generate an FRP from a Kind with symbolic *weights* as there
is no way to generate the values.

## Functions for Working with Symbols

+ `is_symbolic(x)` :: returns true if `x` is a symbolic expression

+ `gen_symbol()` :: returns a unique symbol name every time it is called

+ `symbols(names)` takes a string of space-separated names and returns a tuple
      of symbols with those names. Supports automatically numbered symbols with
      a `...` pattern.

   Examples:
   - `symbols('a b c')`
   - `symbols('a1 a2 ... a10')`

+ `symbol(name)` takes a string and creates a symbolic term with that name

+ `substitute(quantity, mapping)` :: substitutes values from mapping for the
      symbols in `quantity`; mapping is a dictionary associating symbol names with values.
      Not all symbols need to be substituted; if all are substituted with a numeric value
      then the result is numeric.

+ `substitute_with(mapping)` :: returns a function that takes a quantity and substitutes
      with mapping in that quantity.

+ `substitution(quantity, **kw)` :: like `substitute` but takes names and values as
      keyword arguments rather than through a dictionary.
      
  Example: `substitution(symbol('a') + symbol('b'), a=10, b=100)` returns 110.
