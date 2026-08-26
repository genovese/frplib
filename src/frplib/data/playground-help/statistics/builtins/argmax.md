# ArgMax

The `ArgMax` statistic accepts a tuple of positive dimension and returns the
index (0-based) of the component with the maximum value. If more than one
element equals this maximum value, it returns the first.
It gives an error for an empty tuple.

Examples:

+ `ArgMax(1, 2, 3, 4)` => <3>
+ `ArgMax(1, -1, 0)` => <0>
+ `ArgMax(-1, 2, 33, -4)` => <2>
