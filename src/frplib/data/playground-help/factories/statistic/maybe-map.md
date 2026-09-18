# MaybeMap

The statistic factory `MaybeMap` returns statistics that apply a
statistic to every input component, keeping those whose value is not
nothing/None.

The calling signature is `MaybeMap(stat, pad=nothing)` where `stat`
is a statistic and `pad` is an optional quantity that defaults to
`nothing`.

This acts as a combination of ForEach and Keep. Like ForEach, it
applies a statistic to each component, joining the returned value
into the final tuple. Like Keep, it can elect to not include the
value for a component based on the returned value, but whereas Keep
uses a predicate, MaybeMap keeps the result for a component if the
value returned by the statistic is a 1-dimensional tuple or scalar
that is not `nothing` (or `None`).

The returned statistic applies the given statistic to each component
of the input tuple. Components for which it returns a value (scalar
or 1-dim tuple) of `nothing` (or None) are excluded; the rest are
joined together into the output tuple.

However, this preserves the dimension of the tuples, filling out the
final components with the value of `pad`. The number of padded
components equals the number of excluded components times the
dimension of the statistic. (This assumes and implicitly requires
our ordinary constraint that the statistic return output of a fixed
dimension for each input dimension.) As a result, the output tuple
will have the same dimension regardless of how many values are
excluded by the statistic. This may fail if the output dimension
cannot be determined from either the statistic or the mapped values.
(This is another reason to provide a dimension when appropriate for
your statistics.)

If `pad` is set to None, then no such padding is done. Use this
option with care, as transformation of Kinds and FRPs expects the
dimension to be preserved.

Examples (using * to denote nothing):

Define
```python
   def NothingUnless(cond, stat=Id):
       return IfThenElse(cond, stat, nothing)
```

Then:

+ `MaybeMap(NothingUnless(Scalar % 2 == 0))(1, 2, 3, 4)` == <2, 4, *, *>
+ `MaybeMap(NothingUnless(Scalar % 2 == 0), pad=None)(1, 2, 3, 4)` == <2, 4>
+ `MaybeMap(Scalar % 2 != 0, pad=-1)(1, 2, 3, 4)` == <1, 1, -1, -1>
+ Setting `odd_double = NothingUnless(Scalar % 2 != 0, 2 * __)`
  `MaybeMap(odd_double, pad=-1)(1, 2, 3, 4)` == <2, 6, -1, -1>
+ Setting `pos_square = NothingUnless(__ > 0, __ ** 2)`
  `MaybeMap(pos_square, pad=0)(-20, 2, -2, 10, 20)` == <4, 100, 400, 0, 0>
+ If we define a statistic
  ```python
    @statistic(codim=1, dim=3)
    def repeat3(v):
        if v > 0:
            return (v, v, v)
        return nothing

  MaybeMap(repeat3)(1, -4, 4, 0, 10) == <1, 1, 1, 4, 4, 4, 10, 10, 10>
  ```
