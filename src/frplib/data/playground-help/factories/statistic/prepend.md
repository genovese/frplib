# Prepend

The statistic factory `Prepend` returns a statistic that prepends (joins at front) one
or more specified values to its input tuple. It accepts a tuple of
any dimension. `Prepend()` is just the identity statistic.

Examples

+ `tup(1, 2, 3) ^ Prepend(4)` => <4, 1, 2, 3>
+ `tup(1, 2, 3, 4) ^ Prepend(4, 5, 6)` => <4, 5, 6, 1, 2, 3, 4>
+ `tup(10, 20) ^ Prepend(4, 5, 6)` => <4, 5, 6, 10, 20>
+ `tup(1, 2) ^ Prepend()` => <1, 2>
+ `tup(1, 2, 3) ^ Prepend()` => <1, 2, 3>
