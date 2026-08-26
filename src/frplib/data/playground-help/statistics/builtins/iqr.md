# IQR - Interquartile range

The statistic `IQR` accepts any tuple of dimension 4 or greater
and returns a scalar.
It computes the difference between the 75th and 25th quantile,
called the interquartile range
This uses what is called the type 6 definition of interquartile range.

Examples

+ `IQR(1, 2, 3, 4)` => <1>
+ `IQR(1, 1, 1, 1, 1)` => <0>
+ `IQR(tup(k for k in range(1, 100)))` => <50>
