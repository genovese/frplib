# Append

The statistic factory `Append` returns a statistic that appends one
or more specified values to its input tuple. It accepts a tuple of
any dimension. `Append()` is just the identity statistic.

Examples

+ `tup(1, 2, 3) ^ Append(4)` => <1, 2, 3, 4>
+ `tup(1, 2, 3, 4) ^ Append(4, 5, 6)` => <1, 2, 3, 4, 4, 5, 6>
+ `tup(10, 20) ^ Append(4, 5, 6)` => <10, 20, 4, 5, 6>
+ `tup(1, 2) ^ Append()` => <1, 2>
+ `tup(1, 2, 3) ^ Append()` => <1, 2, 3>
