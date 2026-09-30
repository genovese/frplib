# Negate

The `Negate` statistic negates every component of a value.
It accepts a tuple of any dimension.
Note that this is equivalent to `(-1 * __)`, but it 
is sometimes more readable.

Examples

+ `Negate(1, 2, 3, 4)` => <-1, -2, -3, -4>
+ `Negate(1, symbol('a'), 3, nothing)` => <-1, -1 * a, -3, nothing>
+ `Negate(-1, -1, 0, 1, 1)` => <1, 1, 0, -1, -1>
+ `Compose(Negate, Log2, scalar_statistic(k.kernel))`
