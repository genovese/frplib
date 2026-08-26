# as_scalar

`as_scalar(x)` returns a scalar (as a quantity, not a tuple) if `x`
is a scalar or a 1-dim VecTuple, else None.

In the case of a 1-dimensional VecTuple, the scalar is extracted and returned as a quantity.
