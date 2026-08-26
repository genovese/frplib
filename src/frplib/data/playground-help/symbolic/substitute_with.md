# substitute_with

`substitute_with(mapping)` :: returns a function that takes a quantity and substitutes
with mapping in that quantity.

Not all symbols need to be substituted; if all are substituted with
a numeric value then the result is numeric.

Example:
```
    a, b = symbols('a b')
    f = substitute_with({'a': 10, 'b': 100})
    f(a + b)
```
produces 110.
