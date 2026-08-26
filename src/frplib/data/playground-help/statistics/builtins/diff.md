# Diff

The statistic `Diff` accepts a tuple of any dimension > 2 and returns
a tuple of one smaller dimension containing the successive pairwise
differences between the components.

The first component of the result of `Diff(v)` is `v[1] - v[0]`;
the second component is `v[2] - v[1]`, and so forth.

Examples

+ `Diff(1, 2, 3, 4)` => <1, 1, 1>
+ `Diff(10, 10, 10, 10, 10)` => <0, 0, 0, 0>
+ `Diff(1, 4, 9, 16)` => <3, 5, 7>
