# ArgMin

The `ArgMin` statistic accepts a tuple of positive dimension and returns the
index (0-based) of the component with the minimum value. If more than one
element equals this minimum value, it returns the first.
It gives an error for an empty tuple.

Examples:

+ `ArgMin(1, 2, 3, 4)` => <0>
+ `ArgMin(1, -1, 0)` => <1>
+ `ArgMin(-1, 2, 33, -4)` => <3>
