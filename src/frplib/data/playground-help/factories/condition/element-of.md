# ElementOf

The condition factory `ElementOf` returns a condition
that tests for membership in a collection of values.

Values are specified with a single iterable argument containing
the values, or with more than one arguments. In both cases, all
individual values are converted to vec_tuples.

Examples:
+ `ElementOf(1, 2, 3)` returns true for 1, 2, or 3 as scalars or tuples.
+ `ElementOf((1, 2), (3, 4), (5, 6))` returns true for values (1, 2),
  (3, 4), or (5, 6), false otherwise.
+ `ElementOf([(1, 2), (3, 4), (5, 6)])` is equivalent to the last case.
