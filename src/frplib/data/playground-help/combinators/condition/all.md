# All

`All` is a statistic combinator that takes a (scalar) condition
and gives a condition that is true when that condition is true
for every component of the input.

Examples

+ `All(Scalar % 2 == 0)` => true when all components are even
+ `All(2 * Scalar ** 2 - Scalar + 10 > 0)` => true when all components x satisfy 2x^2 - x + 10 > 0.

