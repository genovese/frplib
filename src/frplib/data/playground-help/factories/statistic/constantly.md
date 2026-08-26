# Constantly

The statistic factory `Constantly` returns a statistic that always
returns the specified value. Specifically, `Constantly(a)` is the
statistic that always returns `a`. Constantly accepts a tuple of any
dimension. The statistics it returns also accept any dimension
input, but of course that input is ignored.

Some statistic combinators, like `Fork`, `ForEach`, and `IfThenElse`
automatically wrap constant values in `Constantly` to produce a statistic.

Examples

+ `tup(1, 2, 3) ^ Constantly(1)` => <1>
+ `tup(1) ^ Constantly(4)` => <4>
+ `tup(1, 2, 3) ^ Constantly()` => <>
+ `tup(1, 2, 3) ^ Constantly(10, 100, 1000, 10000)` => <10, 100, 1000, 10000>
