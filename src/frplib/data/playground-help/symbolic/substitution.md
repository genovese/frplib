# substitution

`substitution(quantity, **kw)` is like `substitute`, but instead of taking
a dictionary, it takes names and values.
      
Not all symbols need to be substituted; if all are substituted with
a numeric value then the result is numeric.

Examples: 

+ `substitution(symbol('a') + symbol('b'), a=10, b=100)` returns 110.
+ `substitution(symbol('a') + symbol('b'), a=10)` returns the symbolic expression 10 + b.
