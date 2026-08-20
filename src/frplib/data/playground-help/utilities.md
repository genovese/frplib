# Utilities

**frplib** includes a variety of utility functions to make common
computations easier. These functions are divided into several categories
as shown below. You can get detailed on each of these functions at
lower levels in the info hierarchy.

## Vector Tuple and Quantity Helpers

+ `tup` :: converts arguments to a quantitative vector tuple, whose values are
      numeric or symbolic quantities and can be added or scaled like vectors.

+ `as_scalar` :: converts a 1-dimensional tuple to a scalar

+ `as_quantity` :: converts to a quantity, takes symbols, strings, or numbers.

+ `as_float` :: converts high-precision decimal tuples to Python floats,
      and 1-dimensional tuples to scalar floats.

+ `as_numpy` :: converts high-precision decimal tuples to a numpy float array

## Sequence Helpers

+ `irange` :: create inclusive integer ranges with optional gaps

+ `index_of` :: find the index of a value in a sequence

+ `index_where` :: find the index in a sequence where a predicate is first True

+ `every(f, iterable)` :: returns true if `f(x)` is truthy for every `x` in `iterable`

+ `some(f, iterable)` :: returns true if `f(x)` is truthy for some `x` in `iterable`

+ `lmap(f, iterable)` :: returns a *list* containing `f(x)` for every `x` in `iterable`

+ `fold(f, init, inputs)` :: folds an input sequence using the folding function `f` from the
                             initial accumulator `init`

+ `fold1(f, ilist)` :: folds a non-empty input list using the folding function `f` using
                       the first element of the list as the initial accumulator.
                       The input elements and accumulators have the same type.

+ `frequencies(iterable, counts_only=False)` :: computes counts of
   unique values in iterable; returns a dictionary, but if
   `counts_only` is True, return just the counts without labels

## Function Helpers

+ `identity` :: a function that returns its argument as is

+ `const(a)` :: returns a function that itself always returns the value `a`

+ `compose(f,g)` :: returns the function `f` after `g`

+ `iterate(f, n, start)` :: returns nth item in sequence `start, f(start), f(f(start)), ...`

+ `iterates(f, n, start)` :: returns sequence of first n items from `start, f(start), f(f(start)), ...`

## Output Helpers

+ `show(x)` :: displays an object, list, or dictionary in a more friendly manner.
    See subtopic `show`.
