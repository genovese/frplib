# Projections

Projections are statistics that extract components out of tuples.
These are created with the `Proj` factory.

`Proj` can accept values either between () or [], e.g., `Proj(2, 4)` or `Proj[2, 4]`.
These are interchangeable, though we will use the [] notation here.

The values passed to `Proj` in this way represent the indices (starting at **1**)
of the components that are *kept* in the result. 

Examples:
+ `Proj[1]`
+ `Proj[2, 4]`
+ `Proj[2:5]`
+ `Proj[-1]`
+ `Proj[1, 3 , -1]`
+ `Proj[(1, 3 , -1)]`
+ `Proj([1, 3 , -1])`

The indices passed to `Proj` can be given in a variety of forms:

+ As a list of individual indices, like `2, 4` or `1, 3, 5`.
  These can include negative indices, which count from the end.
  So -1 is the last component, -2 the second to last, and so forth.
+ A single iterable, like a list or tuple, containing such a sequence
  of indices, e.g., `[1, 3, 5]` or `(2, 4)`.
+ A *slice* `a:b` which includes all components from `a` up to but not including `b`.
+ A stepped slice `a:b:s` which includes components from `a` up to but not including
  `b` but stepping by `s`.
+ If either value is excluded in a slice, e.g., `[:4]` or `[3:]`, then the slice
  extends to the beginning or end, respectively.
+ Slices can include negative values as well, so `[:-2]` includes all but the
  last two components.
  
You can also take projections by directly indexing a kind or FRP.
So, the following are all equivalent:
```
   Proj[2, 4](X)
   Proj(2, 4)(X)
   X ^ Proj[2, 4]
   X[2, 4]
```
