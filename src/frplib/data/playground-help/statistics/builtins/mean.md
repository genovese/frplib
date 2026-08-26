# Mean

The `Mean` statistic computes the average of the components of its input tuple.
It accepts a tuple of positive dimension or gives an error message otherwise.

Examples

+ `Mean(1, 2, 3, 4)` => <2.5>
+ `Mean(1, 1, 1, 1, 1)` => <1>
+ `Mean(100, 1000, 1900)` => <1000>
