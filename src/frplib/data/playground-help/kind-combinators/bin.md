# bin

`bin(scalar_kind, lower, width)` returns a kind similar to that
given but with values binned in specified intervals.

The bins are intervals of width `width` starting at `lower`.  So, for instance,
one interval is `lower` to `lower` + `width`.

The given kind should be a scalar kind, or an error is raised.
