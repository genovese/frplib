# substitute

`substitute(quantity, mapping)` substitutes values for the symbols in `quantity`. 
Here,  `mapping` is a dictionary associating symbol names with values.

Not all symbols need to be substituted; if all are substituted with
a numeric value then the result is numeric.

Examples: 
+ `substitute(symbol('a') + symbol('b'), {'a': 10, 'b': 100})` returns 110.
+ `substitution(symbol('a') + symbol('b'), {'a': 10})` returns the symbolic expression 10 + b.
