# Kind Procedures

Procedures provide a clear and compact way to create Kinds that
combine many different operations. As an alternative to operator
style, procedures provide a different perspective that does
not get unduly complicated when it involves many operations.

The `@kind` decorator on a function signals a Kind procedure.
Here's a simple example
```python
    @kind
    def t():
        x = yield uniform(1, 2, 3)
        return x * x
```
This defines a *Kind* `t`, not a function.
The `= yield` is a special operation that draws
all the possible values from the Kind at the right
and binds them to the variable on the left.
You can interpret this as saying that
"for every value `x` from the Kind, make a new
Kind with value `x * x`".
The weights for the produced Kind are tracked automatically
and added together for any values that are the same.
The result in this case is the Kind `uniform(1, 2, 3) ^ (__ ** 2)`.
Another example.
```python
    @kind
    def r():
        x = yield uniform(1, 2, 3)
        y = yield uniform(-1, 0, 1, 10)
        return x + y
```
This produces a Kind `r`.
It draws all the possible values from `uniform(1, 2, 3)`
and all the possible values from `uniform(-1, 0, 1, 10)`.
Each possible `x` is paired with each possible `y`,
and the produced Kind has corresponding `x + y`.
Again, the weights are tracked and combined as needed in the background.
This `r` is equivalent to
```
(uniform(1, 2, 3) * uniform(-1, 0, 1, 10)) ^ Sum
```
Remember: `r` is a Kind, not a function.

We can yield from Kinds we've already defined
or specify the Kinds directly.
```python
    k = choice(10, 20)

    @kind
    def u():
        x = yield k
        y = yield symmetric(1, 2, ..., 17, around=10)
        z = yield r    # r defined above
        
        return (2 * x + 3 * y,  z * z)
```

Kind procedures can return tuples, and these
are converted by `frplib` to vector tuples.
If any of the components are already tuples,
the result is flattened into a proper value.
This is convenient with operations that use joins.
For example:
```python
    a = binary() ** 3
    b = choice(-2, 0, 2) ** 2

    @kind
    def c():
        a = yield A
        b = yield B

        return (a, b)
```
This Kind `c` is five-dimensional.

The `given` operator can be use on the right side of a `yield`
to enforce an observational constraint:
```python
    @kind
    def v():
        s = yield uniform(1, 2, ..., 10)
        yield given(s > 7)
        return a
```
`v` is the Kind `uniform(1, 2, ..., 10) | (__ > 7)`
in operator terms.

Kind procedures can freely mix and match all of these
type of steps, which makes them convenient to use
for complicated systems.
