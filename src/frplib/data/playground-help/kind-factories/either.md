# either

`either(a, b, weight_ratio)`  returns a kind on two values `a` and `b`
with weights `weight_ratio` on `a` and 1 on `b`.
If `weight_ratio` is not supplied, it defaults to 1.

The values `a` and `b` can be numeric or symbolic (or a mixture),
but must have the same dimension.
