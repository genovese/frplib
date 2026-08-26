# Sqrt

The `Sqrt` statistic accepts a tuple *dimension 1* and
returns a scalar tuple containing the square root of its input.
This gives an error when given a tuple of dimension > 1 or 0
or when the input scalar is negative.

To get the square root of all components of a value `v`,
use the `ForEach` statistic combinator: `ForEach(Sqrt, v)`.

Examples:

+ `Sqrt(5)` => <2.236067977499789696409173669>
+ `Sqrt(4)` => <2>
+ `Sqrt(1)` => <1>
+ `Sqrt()` => Error message: `A function (probably a Statistic or conditional Kind/FRP) expects one scalar argument 0 given.`
