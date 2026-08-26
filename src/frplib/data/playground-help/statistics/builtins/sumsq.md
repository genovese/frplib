# SumSq

The `SumSq` statistic accepts a tuple of positive dimension and
returns a scalar tuple containing the sum of squares of
the components. It gives an error when given the empty tuple.

If `v = <v_1, v_2, ..., v_n>`, then `SumSq(v)`
equals `v_1 * v_1 + v_2 + v_2 + ... + v_n * v_n`.
`SumSq` is equivalent to the satistic `Abs * Abs`.

Examples:

+ `SumSq(5)` => <25>
+ `SumSq(-4)` => <16>
+ `SumSq(3, 4)` => <25>
+ `SumSq(1, 1, 1, 1)` => <4>
+ `SumSq(0, 0, 0)` => <0>
+ `SumSq()` => Error message: `A function expects input of dimension at least 1 but 0 was given.`
