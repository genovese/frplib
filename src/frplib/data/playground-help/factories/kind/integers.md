# integers

A Kind factory that represents a choice over integer values from `start` to `stop` by `step`.

If `stop` is None, then the values go from 0 to `tart`. Otherwise, the values
go from `start` up to but not including `stop`.

The `weight_fn` argument (default the constant 1) should be a function; it is
applied to each integer to determine the weights.
