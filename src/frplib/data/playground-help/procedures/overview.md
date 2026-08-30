# Procedures for Creating Kinds and FRPs 

Kind and FRP procedures are specified by
decorating a function definition with `@kind` 
or `@frp`. The resulting construct defines
a Kind or FRP -- **not** a function.
For example:
```python
    @kind
    def t():
        x = yield uniform(1, 2, 3)
        return x * x
```
or
```python
    @frp
    def R():
        s = yield uniform(1, 2, ..., 10)
        yield given(s > 7)
        return a
```

The `yield` keyword is used to bind values
from FRPs and Kinds, and `yield given`
is used to define constraints with observations.
The decorated functions for procedures should
be "generator functions", meaning that they
have at least one `yield` statement.

The decorated functions should take no required
arguments. However, they can take arguments
with default values. The reason for this
is that functions defined in loops in Python
will be looked up at the time the function 
is called (typically after the loop)
rather than at definition time.
However, default argument definitions are bound
at definition time.
For example:
```python
   collected = []
   for i in range(9):
       @kind
       def k(shift=i):
           x = yield uniform(1, 2, ..., 10)
           return x + i

       collected.append(k)
```
produces a list with nine distinct Kinds.


See *Kinds::Kind Procedures*, *FRPs::FRP Procedures*,
*Conditional Kinds::Conditional Kind Procedures*, and *Conditional FRPs::Conditional FRP Procedures*
for more detail.
