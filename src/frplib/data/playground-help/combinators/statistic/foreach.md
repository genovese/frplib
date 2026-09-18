# ForEach

The `ForEach` combinator takes a statistic and creates a new
statistic that applies the given statistic to successive,
non-overlapping chunks of the input tuple.

The full signature is `ForEach(s, by=None, strict=True)`.

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
length of the input. If `strict` is true, the chunk size is chosen
to evenly divide the input tuple's dimension. If `strict` is not
true, then the chunk size is chosen so the residual chunk at the end
is compatible with the codimension of `s`. If no such chunk size can
be found, an error is raised.

So if `s` is a statistic that accepts scalar inputs and `by` is 1 or
not supplied, then `ForEach(s)` applies `s` to each component of its
input tuple, mapping `<v1, v2, ..., vn>` to `<s(v1), s(v2), ..., s(vn)>`,
where the results of the statistics are concatenated into a single tuple.

Otherwise, if the chunk size is k > 1 and `strict` is true, then
`ForEach(s)` maps `<v1, v2, ..., v_nk>` to
`<s(v_1,...,v_k), s(v_k+1,...,v_2k), ..., s(v_(n-1)k+1, ..., v_nk)>`.
If `strict` is not true, then `ForEach(s)` maps
`<v1, v2, ..., v_nk, v_nk+1, ..., v_nk+d>` to
`<s(v_1,...,v_k), ..., s(v_(n-1)k+1, ..., v_nk), s(v_nk+1,...,v_nk+d)>`.

If `s` is a non-statistic callable, it is converted to a statistic.
If `s` is a constant, it is converted to a statistic by applying
Constantly, and `ForEach(Constantly(s))` maps
`<v1, v2, ..., vn>` to `<s, s, ..., s>`, where the latter tuple also has dimension `n`.

Examples:

+ `tup(-10, 20, -3) ^ ForEach(Abs)` => <10, 20, 3>
+ `tup() ^ ForEach(s)` => <>
+ `ForEach(__ ** 2)(1, 2, 3)` == <1, 4, 9>
+ `ForEach(__ + 3)(1, 2, 3)` == <4, 5, 6>
+ `ForEach(1)(1, 2, 3, 4)` == <1, 1, 1, 1>
+ `ForEach((1, 2, 3))(10, 11, 12)` == <1, 2, 3, 1, 2, 3, 1, 2, 3>
+ `tup(1, 2, 3, 4, 5, 6, 7, 8) ^ ForEach(Proj[4])` == <4, 8>
+ `tup(1, 2, 3, 4, 5, 6, 7, 8) ^ ForEach(Proj[1], by=4)` == <1, 5>
+ `tup(1, 2, 3, 4, 5, 6, 7, 8) ^ ForEach(Proj[2], by=4)` == <2, 6>
+ `tup(1, 2, 3, 4, 5, 6, 7, 8) ^ ForEach(Proj[3], by=4)` == <3, 7>
+ `tup(irange(1, 12)) ^ ForEach(Permute(3, 1, 2))` == <3, 1, 2, 6, 4, 5, 9, 7, 8, 12, 10, 11>
+ `tup(1, 2, 3, 4, 5, 6, 7, 8) ^ ForEach(swap)` == <2, 1, 4, 3, 6, 5, 8, 7>
  where
      `swap = statistic(lambda x, y: (y, x), dim=2, description='swaps two components of a pair')`
+ `tup(irange(1, 9)) ^ ForEach(Sum, by=2, strict=False)` == <3, 7, 11, 15, 9>
+ `tup(irange(1, 8)) ^ ForEach(Sum, by=2)` == <3, 7, 11, 15>
+ `tup(irange(1, 9)) ^ ForEach(Sum, by=2, strict=False)` raises an error
   because there is one chunk left over that has size less than 2.
