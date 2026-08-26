# Exp

The `Exp` statistic computes the exponential function. `Exp(x)` is `e^x`,
where `e = 2.71828...`.  It accepts a scalar tuple and returns a scalar tuple.
It gives an error when passed an argument with dimension > 1 or dimension 0.

Examples:
+ `Exp(0)` => <1>
+ `Exp(1)` => <2.718281828459045235360287471>
+ `Exp(-1)` => <0.3678794411714423215955237702>
+ `Exp(Log(10))` => <10.000000000000000000000000>
