# ForEachIndexed

The `ForEachIndexed` combinator takes a statistic and creates a new
statistic that applies the given statistic to successive,
non-overlapping chunks of the input tuple, each prepended
by the (chunk) index (0-based).

The full signature is `ForEachIndexed(s, by=None, strict=True)`.

The returned tuples from all applications of the statistic are
joined into a single larger tuple.

The chunk size is determined by the `by` argument, if supplied, the
codimension of the statistic `s`, and the length of the input.

If `by` is supplied, it should be a positive integer that is
compatible with the codimension of the statistic `s`, meaning that
`s` should accept tuples of dimension `by`. If `strict` is true (the
default), then `by` should also evenly divide the input tuple's
dimension, as this requires the input to be partitioned into
equal-size chunks. If `strict` is not true, chunks of size `by` are
used up to possibly the last chunk. Any residual chunk at the end
must be compatible with the codimension of `s`. If `s` or the input
are incompatible with `by`, an error is raised.

If `by` is not supplied, the chunk size is the smallest number that
is consistent with the the codimension of the statistic `s` and the
length of the input (accounting for the extra dimension taken by the
index). If `strict` is true, the chunk size is chosen to evenly
divide the input tuple's dimension. If `strict` is not true, then
the chunk size is chosen so the residual chunk at the end is
compatible with the codimension of `s`. If no such chunk size can be
found, an error is raised.

So if `s` is a statistic that accepts scalar inputs and `by` is 1 or
not supplied, then `ForEachIndexed(s)` applies `s` to each component of its
input tuple, mapping `<v1, v2, ..., vn>` to `<s(0, v1), s(1, v2), ..., s(n-1, vn)>`,
where the results of the statistics are concatenated into a single tuple.

Otherwise, if the chunk size is k > 1 and `strict` is true, then
`ForEachIndexed(s)` maps `<v1, v2, ..., v_nk>` to
`<s(0, v_1,...,v_k), s(1, v_k+1,...,v_2k), ..., s((n-1)k, v_(n-1)k+1, ..., v_nk)>`.
If `strict` is not true, then `ForEachIndexed(s)` maps
`<v1, v2, ..., v_nk, v_nk+1, ..., v_nk+d>` to
`<s(v_1,...,v_k), ..., s(v_(n-1)k+1, ..., v_nk), s(v_nk+1,...,v_nk+d)>`.

If `s` is a non-statistic callable, it is converted to a statistic.
If `s` is a constant, it is converted to a statistic by applying
Constantly, and `ForEachIndexed(Constantly(s))` maps
`<v1, v2, ..., vn>` to `<s, s, ..., s>`, where the latter tuple also has dimension `n`.

Examples:

+ `tup(-10, 20, -3) ^ ForEachIndexed(Abs)` => <10, 20, 3>
+ `tup() ^ ForEachIndexed(s)` => <>
+ `ForEachIndexed(__ ** 2)(1, 2, 3)` == <0, 1, 1, 4, 4, 9>
+ `ForEachIndexed(__ + 3)(1, 2, 3)` == <3, 4, 4, 5, 5, 6>
+ `ForEachIndexed(1)(1, 2, 3, 4)` == <1, 1, 1, 1>
+ `ForEachIndexed(swap)(11, 21, 31, 41)` == <11, 0, 21, 1, 31, 2, 41, 3>


