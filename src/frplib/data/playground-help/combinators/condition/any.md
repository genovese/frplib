# Any

`Any` is a statistic combinator that takes a (scalar) condition
and gives a condition that is true when that condition is true
for at least one component of the input.

Examples

+ `Any(Scalar % 2 == 0)` => true when at least one components are even
+ `Any(2 * Scalar ** 2 - Scalar + 10 > 0)` => true when at least one components x satisfy 2x^2 - x + 10 > 0.
