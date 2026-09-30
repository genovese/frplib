# Between

`Between(a, b)` is a condition factory. The returned condition tests whether its input
lies between bounds `a` and `b`, optionally including the upper bound `b`.

+ `Between(a, b)` tests its input `v` satisfies `a <= v and v < b`.
+ `Between(a, b, inclusive=True)` tests its input `v` satisfies `a <= v and v <= b`.

Note that for values of dimension bigger than 1, the test `v < b` is true
if *some component* of `v` is less than the corresponding component of `b`
and *all components` of `v` are less than or equal to their corresponding component
of `b`.

The returned statistic can be easily reproduced using a statistic
expression, e.g., `And(a <= __,  __ < b)`, but this factory is provided
for convenience and readability, including when combined with `Not`.


Examples

+ `tup(4, 5, 6, 7, 9) ^ Between(4, 10)` is true.

+ `tup(4, 5, 6, 7, 10) ^ Between(4, 10)` is true.

+ `tup(10, 10, 10, 10, 10) ^ Between(4, 10)` is false.

+ `tup(10, 10, 10, 10, 10) ^ Between(4, 10, True)` is true.

+ `Between(4, 10)(3)` is false.

+ `Between(4, 10)(4)` is true.

+ `Between(4, 10)(10)` is false.

+ `Between(4, 10, True)(10)` is true.
