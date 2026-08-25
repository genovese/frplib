# choice

`choice(a, b, weight_ratio)`  returns a kind on two values `a` and `b`
with weights 1 on `a` and `weight_ratio` on `b`.
If `weight_ratio` is not supplied, it defaults to 1.

The values `a` and `b` can be numeric or symbolic (or a combination),
but must have the same dimension.

Examples:
  + `choice(0, 1)`
  + `choice(0, 1, 4)`
  + `choice(0, 1, '1/4')`
  + `choice(0, 1, 0.25)`
