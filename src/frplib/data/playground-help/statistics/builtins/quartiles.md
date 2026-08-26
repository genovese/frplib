# Quartiles

The statistic `Quartiles` accepts any tuple of dimension 4 or greater.
It computes the three quartiles (25%, 50% or median, and 75%)
and returns the 3-dimensional tuple.

Examples

+ `Quartiles(1, 2, 3, 4)` => <2, 2.5, 3>
+ `Quartiles(1, 1, 1, 1, 1)` => <1, 1, 1>
+ `Quartiles(tup(k for k in range(1, 100)))` => <25, 50, 75>
