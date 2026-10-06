# All

`All` is a statistic combinator that takes a condition
and gives a condition that is true when that condition is true
for all successive chunks of the input.

The signature looks like
```python
    All(cond)
    All(cond, by=n)
```

The chunk size is determined by the `by` argument, if supplied,
the codimension of the statistic `s`, and the length of the input.

If `by` is *not* supplied, the chunk size is the smallest number
that is consistent with the the codimension of the statistic `s`
and the length of the input. The chunk size is chosen to evenly
divide the input tuple's dimension. If no such chunk size can be
found, an error is raised.

If `by` is supplied, it should be a positive integer that is
compatible with the codimension of the statistic `s`, meaning
that `s` should accept tuples of dimension `by`. The `by` should
also evenly divide the input tuple's dimension, as this requires
the input to be partitioned into equal-size chunks. If `s` or
the input are incompatible with `by`, an error is raised.

Once the chunk size is determined, All applies `cond` to each
such chunk (as a VecTuple) and returns true if all the results
are true. As usual for a condition, True is <1> and False is
<0>.

Examples
+ `All(Scalar % 2 == 0)` => true when all components are even
+ `All(2 * Scalar ** 2 - Scalar + 10 > 0)` => true when all components x satisfy 2x^2 - x + 10 > 0.
+ `is_true(tup(1, 3, 2, 1) ^ All(__ > 0))`
+ `is_false(tup(1, 3, 0, 1) ^ All(__ > 0))`
+ `is_true(tup(1, 1, 2, 2, 3, 3, 4, 4) ^ All(Proj[1] == Proj[2]))`
+ `is_false(tup(1, 1, 2, 2, 8, 3, 4, 4) ^ All(Proj[1] == Proj[2]))`
+ `is_true(tup(1, 1, 2, 2, 3, 3, 4, 4) ^ All(Proj[1] == Proj[2], by=4))`
+ `is_false(tup(1, 1, 2, 2, 3, 3, 4, 4) ^ All(Proj[1] == Proj[3], by=4))`
