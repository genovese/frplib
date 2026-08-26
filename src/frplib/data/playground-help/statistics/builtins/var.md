# Variance

The `Variance` statistic computes the sample variance of the
components of its input tuple. This is the sum of squares
of the deviations of the components from the component mean
divided by dimension - 1. It accepts a tuple of positive
dimension or gives an error message otherwise.

Examples

+ `Variance(1, 2, 3, 4)` => <1.666666666666666666666666667>
+ `Variance(1, 1, 1, 1, 1)` => <0>
+ `Variance(100, 1000, 1900)` => <810000>
