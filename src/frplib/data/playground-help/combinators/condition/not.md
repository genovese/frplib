# Not

The Python `not` operation works only for Python bools and so cannot
operate on conditions as a combinator.
For that purpose, `frplib` offers the `Not` combinator.
Note the case!

If `c` is a condition, `Not(c)` is the complementary condition.
It is false for inputs where `c` is true, and vice versa.

Examples

+ `Not(__ >= 0)` => tests whether *all components* of the input are negative
+ `Not(Scalar >= 0)` => tests whether a scalar input is negative
+ `Not(And(__ > 0, __ < 2))` => equivalent to `Or(__ <= 0, __ >= 2)`.
