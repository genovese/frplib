# subsets

The Kind `subsets(col, outside_element=nothing)` represents a
a uniform choice over subsets of a specified collection.

Because the dimension needs to be consistent, outside_element,
a value not in the collection, should be supplied to pad
out the values.  This value should be comparable to the
elements in the collection. This defaults to `nothing`.

The padding elements are placed at the beginning of the tuples
so that the Kind sorts nicely. This may be changed in the future.

Example

`subsets([1, 2, 3])` produces
```
      ,---- 1/8 ---- <□, □, □>
      |---- 1/8 ---- <□, □, 1>
      |---- 1/8 ---- <□, □, 2>
      |---- 1/8 ---- <□, □, 3>
  <> -|
      |---- 1/8 ---- <□, 1, 2>
      |---- 1/8 ---- <□, 1, 3>
      |---- 1/8 ---- <□, 2, 3>
      `---- 1/8 ---- <1, 2, 3>
```
