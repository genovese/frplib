# Abs

The `Abs` statistic accepts a tuple of positive dimension and
returns a scalar tuple containing Euclidean length of the tuple
considered as a vector.

If `v = <v_1, v_2, ..., v_n>`, then `Abs(v)`
is `Sqrt(v_1 * v_1 + v_2 + v_2 + ... + v_n * v_n)`.
If `v` is a scalar, then `Abs(v)` is just the absolute
value of the scalar.

Examples:

+ `Abs(5)` => <5>
+ `Abs(-4)` => <4>
+ `Abs(3, 4)` => <5>
+ `Abs(1, 1, 1, 1)` => <2>
+ `Abs(0, 0, 0)` => <0>
+ `Abs()` => Error message: `A function expects input of dimension at least 1 but 0 was given.`
