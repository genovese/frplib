# permutations_of

The Kind `permutations_of(col, r=None)` represents a
a uniform choice over all permutations of a specified collection.
`col` should be any iterable collection.
The optional `r`, if supplied, should be a positive integer
and corresponds to taking permutations "r-at-a-time",
r-length permutations drawn from the collection.
`r=None` corresponds to `r` equal to the size of the collection



Examples

`permutations_of([1, 2, 3])` produces
```
      ,---- 1/6 ---- <1, 2, 3>
      |---- 1/6 ---- <1, 3, 2>
      |---- 1/6 ---- <2, 1, 3>
  <> -|
      |---- 1/6 ---- <2, 3, 1>
      |---- 1/6 ---- <3, 1, 2>
      `---- 1/6 ---- <3, 2, 1>
```

`permutations_of([1, 2, 3, 4], r=2)`
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
