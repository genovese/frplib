# Symbols and Symbolic Quantities

**frplib** has some facility for manipulating symbolic quantities.
The function `symbol` is used to create symbols with a given name,
typically single letters. You can do arithmetic on symbolic quantities
and (ATTN:coming soon) take functions of them. There is a limited
(though improving) simplification routine that makes symbolic kinds
feasible within reason. The size of the expressions grows quickly,
so it is best to keep this to relatively simple cases.

As an example:
```
a = symbol('a')
k1 = uniform(a, 2*a, 4*a)
k2 = weighted_as(1, 2, 4, weights=[1, a, a**2]) 
```
gives two kinds, one with symbolic values and one with symbolic weights.
(The two cases can be combined, though again keep the caveat above
in mind.)

Expectations of these kinds will be symbolic expressions.

The function `symbols` takes a space-separated sequence
of names and returns a tuple of corresponding symbols.
Numeric sequences of symbols can be specified by
a pair of names with a numeric suffice separated by a '...'.

As an example:
```
x, y, z = symbols('x y z')
u = symbols('u0 ... u9)
```

