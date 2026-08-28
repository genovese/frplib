# ordered_samples

The Kind `ordered_samples(n, x1, x2, ..., xm)` represents a
a uniform choice over all ordered samples of size `n`  items from a
set `{x1, x2, ..., xm}`.

The set of values to sample from can a single iterable
(including generators or iterators) or multiple arguments. This
respects '...' patterns like `weighted_as` and other Kind
factories. Values are converted to quantities, and so can be
symbols or string numbers/fractions (which are converted to
high-precision quantities).

The values of this Kind distinguish between different orders of the
sample. See `without_replacement` for an analogous factory that does
not.

Examples:
+ `ordered_samples(2, 1, 2, 3, 4)`
  Same as `ordered_samples(2, [1, 2, 3, 4])`
```
      ,---- 1/12 ---- <1, 2>
      |---- 1/12 ---- <1, 3>
      |---- 1/12 ---- <1, 4>
      |---- 1/12 ---- <2, 1>
      |---- 1/12 ---- <2, 3>
      |---- 1/12 ---- <2, 4>
  <> -|
      |---- 1/12 ---- <3, 1>
      |---- 1/12 ---- <3, 2>
      |---- 1/12 ---- <3, 4>
      |---- 1/12 ---- <4, 1>
      |---- 1/12 ---- <4, 2>
      `---- 1/12 ---- <4, 3>
```

+ `ordered_samples(3, [1, 2, 3, 4])`
```
      ,---- 1/24 ---- <1, 2, 3>
      |---- 1/24 ---- <1, 2, 4>
      |---- 1/24 ---- <1, 3, 2>
      |---- 1/24 ---- <1, 3, 4>
      |---- 1/24 ---- <1, 4, 2>
      |---- 1/24 ---- <1, 4, 3>
      |---- 1/24 ---- <2, 1, 3>
      |---- 1/24 ---- <2, 1, 4>
      |---- 1/24 ---- <2, 3, 1>
      |---- 1/24 ---- <2, 3, 4>
      |---- 1/24 ---- <2, 4, 1>
      |---- 1/24 ---- <2, 4, 3>
  <> -|
      |---- 1/24 ---- <3, 1, 2>
      |---- 1/24 ---- <3, 1, 4>
      |---- 1/24 ---- <3, 2, 1>
      |---- 1/24 ---- <3, 2, 4>
      |---- 1/24 ---- <3, 4, 1>
      |---- 1/24 ---- <3, 4, 2>
      |---- 1/24 ---- <4, 1, 2>
      |---- 1/24 ---- <4, 1, 3>
      |---- 1/24 ---- <4, 2, 1>
      |---- 1/24 ---- <4, 2, 3>
      |---- 1/24 ---- <4, 3, 1>
      `---- 1/24 ---- <4, 3, 2>
```
