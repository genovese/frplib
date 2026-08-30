# FRP Procedures

Procedures provide a clear and compact way to create FRPs that
combine many different operations. As an alternative to operator
style, procedures provide a different perspective that does
not get unduly complicated when it involves many operations.

The `@frp` decorator on a function signals an FRP procedure.
```python
    @frp
    def Z():
        x = yield frp(uniform(1, 2, 3))
        y = yield frp(uniform(-1, 0, 1, 10))
        return x + y
```
The right side of a yield in an FRP procedure can be an
FRP or a Kind. In the latter case, a fresh FRP is constructed
from the Kind. This procedure says that `Z` gets its value by
first extracting a value from the FRP `frp(uniform(1, 2, 3))` when
it is available, then extracting a value from `frp(uniform(-1, 0, 1, 10))`
when it is available, and then adding them to get the final value.
This defines an ***FRP*** `Z` (not a function)
that gets its value in that way. In operator terms, this
`Z` is equivalent to
```
(frp(uniform(1, 2, 3)) * frp(uniform(-1, 0, 1, 10))) ^ Sum
```

We can yield from FRPs we've already defined
and can use Kinds instead of FRPs on the right side of the `yield`:
```python
    X = choice(10, 20)

    @frp
    def U():
        x = yield X
        y = yield symmetric(1, 2, ..., 17, around=10)
        z = yield Z    # Z defined above
        
        return (2 * x + 3 * y,  z * z)
```

FRP procedures can return tuples, and these
are converted by `frplib` to vector tuples.
If any of the components are already tuples,
the result is flattened into a proper value.
This is convenient with operations that use joins.
For example:
```python
    A = binary() ** 3
    B = choice(-2, 0, 2) ** 2

    @frp
    def V():
        a = yield A
        b = yield B

        return (a, b)
```
This FRP `V` is five-dimensional.

The `given` operator can be use on the right side of a `yield`
to enforce an observational constraint:
```python
    @frp
    def R():
        s = yield uniform(1, 2, ..., 10)
        yield given(s > 7)
        return a
```
`R` is the FRP `frp(uniform(1, 2, ..., 10)) | (__ > 7)`
in operator terms.

You can get the Kind of an FRP defined with a procedure
just like usual, with the `kind` function.
The `clone` function works also just as usual.

FRP procedures can freely mix and match all of these
type of steps, which makes them convenient to use
for complicated systems.
