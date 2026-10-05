# Diffs

The statistic factory `Diffs(m)` returns a statistic that computes
successive `m`-th order differences of its input components. The
resulting tuple has shorter length by `m` components. `Diffs(m)` is
the composition of `Diffs(m - 1)` and `Diffs(1)`. `Diffs(1)` is
equivalent to the builtin statistic `Diff`.

Examples:

+ `tup(1, 2, 4, 9, 16) ^ Diffs(2)` => <1, 3, 2>
+ `tup(1, 2, 4, 9, 16) ^ Diffs(1) ^ Diffs(1)` => <1, 3, 2>
+ `tup(1, 2, 3, 4, 5) ^ Diffs(2)` => <0, 0, 0>
+ `tup(1, 2, 3, 4, 5) ^ Diffs(3)` => <0, 0>
