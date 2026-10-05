# Shift

`Shift` is a statistic factory that takes an integer `m` and returns
a statistic `Shift(m)` that cyclically shifts the components of its
input to the right by the specified amount.

Negative shifts produce a cyclic left shift by the absolute value.
If the shift is 0, this just returns the identity statistic.

Examples
+ `(tup(1, 2, 3, 4, 5) ^ Shift(1)) == tup(5, 1, 2, 3, 4)`
+ `(tup(1, 2, 3, 4, 5) ^ Shift(2)) == tup(4, 5, 1, 2, 3)`
+ `(tup(1, 2, 3, 4, 5) ^ Shift(0)) == tup(1, 2, 3, 4, 5)`
+ `(tup(1, 2, 3, 4, 5) ^ Shift(100)) == tup(1, 2, 3, 4, 5)`
+ `(tup(1, 2, 3, 4, 5) ^ Shift(-1)) == tup(2, 3, 4, 5, 1)`
+ `(tup(1, 2, 3, 4, 5) ^ Shift(-2)) == tup(3, 4, 5, 1, 2)`
+ `(tup(1, 2, 3, 4, 5) ^ Shift(99)) == tup(2, 3, 4, 5, 1)`
+ `(tup(1, 2, 3, 4, 5) ^ Shift(101)) == tup(5, 1, 2, 3, 4, 5)`
+ `(tup(1, 2, 3, 4, 5) ^ Shift(5)) == tup(1, 2, 3, 4, 5)`
+ `(tup(1, 2, 3, 4, 5) ^ Shift(-5)) == tup(1, 2, 3, 4, 5)`
+ `(tup(irange(1, 7)) ^ Shift(6)) == (tup(irange(1, 7)) ^ Shift(-1))`
+ `(tup(irange(1, 7)) ^ Shift(5)) == (tup(irange(1, 7)) ^ Shift(-2))`
+ `(tup(irange(1, 7)) ^ Shift(4)) == (tup(irange(1, 7)) ^ Shift(-3))`
+ `(tup(irange(1, 7)) ^ Shift(3)) == (tup(irange(1, 7)) ^ Shift(-4))`
+ `(tup(irange(1, 7)) ^ Shift(2)) == (tup(irange(1, 7)) ^ Shift(-5))`
+ `(tup(irange(1, 7)) ^ Shift(1)) == (tup(irange(1, 7)) ^ Shift(-6))`
