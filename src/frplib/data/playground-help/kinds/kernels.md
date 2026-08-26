# The Kernel of a Kind

If `k` is a Kind, then `k.kernel` is its ***kernel** function.
This takes any value as an argument and returns a non-negative number.
Specifically, `k.kernel(x)` returns either

+ the canonical weight in the Kind `k` when `x` is a value of `k`, or
+ 0 if `x` is not a value of `k`.

Examples

+ `uniform(1, 2, 3).kernel(1)` => 1/3
+ `uniform(1, 2, 3).kernel(4)` => 0
