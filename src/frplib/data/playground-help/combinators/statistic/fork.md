# Fork

The `Fork` combinator takes multiple statistics
and creates a new statistic that passes its input to all of
the original statistics and concatenates the values they return
into one long tuple.

Specifically, if `s1`, `s2`, ..., `sn` are satistics, then
`Fork(s1, s2, s3, ..., sn)` takes an input value v
and produces the tuple `s1(v) :: s2(v) :: s3(v) :: ... :: sn(v)`,
where the results of the statistics are concatenated into
a single tuple. At least one statistic must be provided.

If any `si` is a constant, it is automatically wrapped in `Constantly`
to produce a statistic representing that value.

Examples

+ `tup(1, 10, -2, 5) ^ Fork(Min, Sum, Product, Max)` => <-2, 14, -100, 10>
+ `tup(1, 2, 3, 4, 5) ^ Fork(0, Diff, Sum)` => <0, 1, 1, 1, 1, 15>
+ `Fork(Id, 1, s1, s2)` => takes `v` to `v :: 1 :: s1(v) :: s2(v)`.
+ `Fork(s)` is the same as `s`

If the statistics given `Fork` are monoidal, the resulting statistic
will be as well. The primary use case for this is in the construction
of fast join powers (cf `fast_join_pow`).
