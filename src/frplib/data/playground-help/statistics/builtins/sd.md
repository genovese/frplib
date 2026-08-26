# StdDev

The `StdDev` statistic computes the sample standard deviation of the
components of its input tuple. It accepts a tuple of positive
dimension or gives an error message otherwise.

Examples

+ `StdDev(1, 2, 3, 4)` => <1.290994448735805628393088467>
+ `StdDev(1, 1, 1, 1, 1)` => <0>
+ `StdDev(100, 1000, 1900)` => <900>
