# symbols

`symbols(names)` takes a string of space-separated names and returns
a *tuple* of symbols with those names. This supports automatically
numbered symbols with a `...` pattern, where the natural numbers are at the
end of the names, like `x_1 ... x_5`.  Because the numbers increase by 1 each
time, you only need a first and a last around the `...`.

 Examples:
 - `symbols('x')`      (Note: A single name is fine but this still returns a tuple.)
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
