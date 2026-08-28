# evenly_spaced

A Kind factory that represents a choice over evenly spaced numbers from `start` to `stop`.
The full signature is
```python
    evenly_spaced(start, stop=None, num=2, by=None, weight_by=const(1))
```
If `stop` is None, then the values go from 0 to `start`. Otherwise, the values
go from `start` up to but not including `stop`.

If `num` < 1 or `by` is supplied and is inconsistent with the direction
of `stop - start` (or just `start` if `stop` is `None`), this returns the empty Kind.

If `by` is not None, then it supersedes `num` and the
sequence goes from start to up to but not over stop (or 0 up to
`start` if `stop` is `None`), skipping by `by` at each step.

Otherwise, the values are a sequence of `start` to `stop` with length `num`.

The `weight_fn` argument (default the constant 1) should be a
function that takes a number; it is applied to each value in the
sequence to determine its weight.

Examples:
+ `evenly_spaced(1, 9, 5)`              # values: 1, 3, 5, 7, 9
+ `evenly_spaced(1, 9, by=3)`           # values: 1, 4, 7
+ `evenly_spaced(0.05, 0.95, by=0.05)`  # 19 values from 0.05, 0.10, ..., 0.95
# `evenly_spaced(100, num=101)`         # values: 0, 1, ..., 100
