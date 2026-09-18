# Keep

The statistic factory `Keep` returns statistics that keeps
components of its input that satisfy a specified predicate.

This has signature `Keep(predicate, pad=nothing)`, where `predicate`
is a condition and `pad` is an optional quantity that defaults to
`nothing`.

The returned statistic applies the condition `predicate`
to each component of the input tuple. Components for which
it returns a truthy value are kept, the rest are removed.

However, this preserves the dimension of the tuples, filling
out the final components with the value of `pad` to the
original dimension. The default value of `pad` is `nothing`,
a special frplib value designed for this purpose that
displays and combines with ordinary values. See the documentation
for `nothing` in frplib.numeric.

If `pad` is set to None, then no padding is done. Use this option
with care, as transformation of Kinds and FRPs expects the dimension
to be preserved.

Examples (using * to denote nothing)

+ `Keep(Scalar % 2 == 0)(1, 2, 3, 4)` == <2, 4, *, *>
+ `Keep(Scalar % 2 != 0, pad=-1)(1, 2, 3, 4)` == <1, 3, -1, -1>
+ `Keep(__ > 0, pad=0)(-20, 2, -2, 10, 20)` == <2, 10, 20, 0, 0>
