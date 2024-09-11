# evenly_spaced

`evenly_spaced(start, stop=None, num: int = 2, by=None, weight_by=lambda _: 1)`

Returns the Kind of an FRP whose values consist of evenly spaced numbers from `start` to `stop`.

If `stop` is not supplied, than values go from 0 to `start`.
Otherwise, the values go from `start` to but not beyond `stop`.
In this case, `stop` can be either less than or greater than `start`.

If num < 1 or by is supplied and is inconsistent with the direction
of stop - start (or start if stop is None), this returns the empty Kind.

Otherwise, if `by` is not None, then it supersedes `num` and the
sequence goes from start to up to but not over stop (or 0 up to
start if stop is None), skipping by `by` at each step.

The `weight_fn` argument (default the constant 1) should be a function; it is
applied to each integer to determine the weights.

Examples:
  + `evenly_spaced(1, 9, 5)`              values 1, 3, 5, 7, 9
  + `evenly_spaced(1, 9, by=3)`           values 1, 4, 7
  + `evenly_spaced(0.05, 0.95, by=0.05)`  19 values from 0.05, 0.10, ..., 0.95
  + `evenly_spaced(0.95, 0.05, by=-0.05)` 19 values from 0.95, 0.90, ..., 0.05
