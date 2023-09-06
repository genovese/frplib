# Utilities

**frplib** includes a variety of utilities to make various
operations easier and to access information from objects
like kinds, FRPs, etc. in a uniform way.

## Cloning

+ `clone(X)` :: produces a copy of its argument `X` if possible; primarily useful with
    FRPs and conditional FRPs, where it produces fresh copies with their own values.

## Property Accessors

+ `dim` :: `dim(x)` returns the dimension of `x`, if available. Note that taking
      the dimension of an FRP may force the kind computation.

+ `codim` :: `codim(x)` returns the codimension of `x`, if available

+ `size` :: `size(x)` returns the size of `x`, usually a kind, if available

+ `values` :: `size(x)` returns the *set* of `x`'s values, if available; applies to kinds


## Symbolic Manipulation

+ `is_symbolic(x)` :: returns true if `x` is a symbolic expression

+ `gen_symbol()` :: returns a unique symbol name every time it is called

+ `symbol(name)` takes a string and creates a symbolic term with that name

+ `substitute(quantity, mapping)` :: substitutes values from mapping for the
      symbols in `quantity`; mapping is a dictionary associating symbol names with values.
      Not all symbols need to be substituted; if all are substituted with a numeric value
      then the result is numeric.

+ `substitute_with(mapping)` :: returns a function that takes a quantity and substitutes
      with mapping in that quantity.

+ `substitution(quantity, **kw)` :: like `substitute` but takes names and values as
      keyword arguments rather than through a dictionary.

## Tuples and Quantities

+ `qvec` :: converts arguments to a quantitative vector tuple, whose values are
      numeric or symbolic quantities and can be added or scaled like vectors.

+ `as_quantity` :: converts to a quantity, takes symbols, strings, or numbers.

## Function Helpers

+ `identity` :: a function that returns its argument as is

+ `const(a)` :: returns a function that itself always returns the value `a`

+ `compose(f,g)` :: returns the function `f` after `g`


## Sequence Helpers

+ `irange` :: create inclusive integer ranges with optional gaps

+ `index_of` :: find the index of a value in a sequence

+ `every(f, iterable)` :: returns true if `f(x)` is truthy for every `x` in `iterable`

+ `some(f, iterable)` :: returns true if `f(x)` is truthy for some `x` in `iterable`

+ `lmap(f, iterable)` :: returns a *list* containing `f(x)` for `x` in `iterable`

## Sub-topics

`symbols`, `irange`, `index_of`
