# Symbolic Manipulation

`frplib` has the ability to represent, manipulate, and simplify
symbolic quantitiess and expressions. The capabilities are somewhat
limited at the moment, but improving. For simple expressions, they
do well, but for long iterative computations, the symbolic
expressions can get complicated.

Symbolic expressions are quantities and can be used for the values
and weights of a Kind and for the values of an FRP. Note that we
cannot generate an FRP from a Kind with symbolic *weights* as there
is no way to generate the values.

As an example:
```
a = symbol('a')
k1 = uniform(a, 2*a, 4*a)
k2 = weighted_as(1, 2, 4, weights=[1, a, a**2]) 
```
gives two Kinds, one with symbolic values and one with symbolic weights.
(The two cases can be combined, as well.)
Expectations of these Kinds will be symbolic expressions.

## Functions for Working with Symbols

+ `symbols(names)` takes a string of space-separated names and returns a *tuple*
  of symbols with those names. This supports automatically
  numbered symbols with a `...` pattern, where the integers are at the
  end of the names, like `x_1 ... x_5`.

   Examples:
   - `symbols('a b c')`
   - `symbols('a1 ... a10')`

   This is often assigned to multiple variables of the same name using
   tuple destructuring:
   ```
       a, b, c = symbols(a, b, c)
       u = symbols('u_0 ... u_10')

       u[0]  # the symbol u_0
       u[9]  # the symbol u_9
   ```

+ `symbol(name)` takes a string and creates a symbolic quantity with that name

+ `is_symbolic(x)` :: returns true if `x` is a symbolic expression

+ `gen_symbol()` :: returns a symbol with a unique name every time it is called

+ `substitute(quantity, mapping)` :: substitutes values from mapping for the
      symbols in `quantity`; mapping is a dictionary associating symbol names with values.
      Not all symbols need to be substituted; if all are substituted with a numeric value
      then the result is numeric.

  Example: `substitute(symbol('a') + symbol('b'), {'a': 10, 'b': 100})` returns 110.

+ `substitute_with(mapping)` :: returns a function that takes a quantity and substitutes
      with mapping in that quantity.

  Example:
  ```
      a, b = symbols('a b')
      f = substitute_with({'a': 10, 'b': 100})
      f(a + b)  #=> returns 110
  ```

+ `substitution(quantity, **kw)` :: like `substitute`, but instead of taking
  a dictionary, it takes names and values. but takes names and values as
      
  Example: `substitution(symbol('a') + symbol('b'), a=10, b=100)` returns 110.
