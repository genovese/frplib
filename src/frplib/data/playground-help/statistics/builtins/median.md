# Median

The `Median` statistic computes the *median* of the components of its input tuple.
This is the middle element in sorted order for odd dimension
and the average of the two middle elements in sorted order for even dimension.
It accepts a tuple of positive dimension or gives an error message otherwise.

Examples

+ `Median(1, 2, 3, 4)` => <2.5>
+ `Median(1, 1, 1, 1, 1)` => <1>
+ `Median(100, 1000, 1900)` => <1000>
