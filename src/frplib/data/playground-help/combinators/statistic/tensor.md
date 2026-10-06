# Tensor

`Tensor` is a statistic combinator that takes the tensor product of
multiple statistics. The resulting statistic applies the given
statistics in order to successive chunks of the input tuple.

A simple use is `Tensor(s1, s2, s3, ..., sn)`. Given an 
input `x1 :: x2 :: x3 :: ... :: xn`, this forms a tuple
`s1(x1) :: s2(x2) :: s3(x3) :: ... :: sn(xn)`.

The key issue here is how the input tuple is partitioned into
chunks. There are three mechanisms for determining the chunk sizes,
in decreasing order of priority.

+ The statistics can be tagged in tuples with codimension
  ranges as either (stat, lo, hi) or (stat, sz).
  The former case says that the chunk size should be between
  lo and hi (inclusive); the latter says the chunk size
  should be exactly sz.

  This looks like
  ```python
      Tensor(s1, (s2, 4), (s3, 1, 10))
  ```
  where here `s1` is untagged, `s2` has chunk size 4,
  and `s3` between 1 and 10 inclusive.

+ The `by` argument

  If `by` is an integer, then all chunks are set to that size.
  If `by` is a list, its entries give the chunk size for the
  corresponding statistics, with None used to indicate no
  constraint. (If `by` is too short, it is extended by None.)

  This looks like
  ```python
      Tensor(s1, s2, s3, by=5)
      Tensor(s1, s2, s3, s4, by=[1, 2, 3, 4])
  ```

+ The statistic's codimension

  The codimension of each statistic determines a range
  of acceptable chunk sizes (lo, hi).

These are used in decreasing order of priority. That is,
tagged bounds take precedence over `by` and both over
the codimensions. A use case for tagging is often
to restrict the allowable range, especially away
from 0 or infinity. See the examples below with Sum.

Given an input of definite length, the chunk sizes
are determined greedily. If there is a statistic with
infinite range, the last of these absorbs all the
surplus above the minimum allowed chunk sizes.
Otherwise, as much of the surplus is used as possible
on successive statistics.

If a quantity or value are given in lieu of a statistic,
it is wrapped in `Constantly` to produce a statistic.
These can also be tagged with codimensions or codimension
bounds in tuples just as with statistics.

Examples
+ (tup(1, 2, 3, 4, 5, 6) ^ Tensor(Proj[1] + 2*Proj[2], Proj[1] + 10*Proj[2] + Proj[3], 100 * __))
    == tup(5, 48, 600)
+ (tup(1, 2, 3, 4, 5, 6, 7, 8) ^ Tensor(Proj[1] + 2*Proj[2], Proj[1] + 10*Proj[2] + Proj[3], 100 * __))
    == tup(5, 48, 600, 700, 800)
+ (tup(1, 2, 3, 4, 5, 6, 7, 8) ^ Tensor(Proj[1] + 2*Proj[2], Proj[1] + 10*Proj[2] + Proj[3], Sum, (100 * __, 1)))
    == tup(5, 48, 13, 800)
+ (tup(1, 2, 3, 4, 5, 6, 7, 8) ^ Tensor(Proj[1] + 2*Proj[2], Proj[1] + 10*Proj[2] + Proj[3], (Sum, 2), 100 * __))
    == tup(5, 48, 13, 800)
+ (tup(1, 2, 3, 4, 5, 6, 7, 8) ^ Tensor(Proj[1] + 2*Proj[2], Proj[1] + 10*Proj[2] + Proj[3], (Sum, 1, infinity), 100 * __))
    == tup(5, 48, 6, 700, 800)
+ (tup(irange(1, 10)) ^ Tensor(Proj[1] + 2*Proj[2], Proj[1] + 10*Proj[2] + Proj[3], 100 * __, by=[4, 4, 2]))
    == tup(5, 72, 900, 1000)
