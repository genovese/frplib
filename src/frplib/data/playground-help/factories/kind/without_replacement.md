# without_replacement

The Kind `without_replacement(n, x1, x2, ..., xm)` represents a
uniform choice over samples without replacement of `n` items from a
set `{x1, x2, ..., xm}`.

The set of values to sample from can a single iterable
(including generators or iterators) or multiple arguments. This
respects '...' patterns like `weighted_as` and other Kind
factories. Values are converted to quantities, and so can be
symbols or string numbers/fractions (which are converted to
high-precision quantities).

The values of this Kind do not distinguish between different orders
of the sample. To get the Kind of samples with order do

    permutations_of // without_replacement(n, xs)

See `ordered_samples` for the factory that does this.

Examples:
+ `without_replacement(2, 1, 2, 3, 4)`
  Same as `without_replacement(2, [1, 2, 3, 4])`

+ `without_replacement(3, [1, 2, 3, 4])`
  Returns Kind that is uniform on <1, 2, 3>, <1, 2, 4>, <1, 3, 4>, <2, 3, 4>

+ `without_replacement(2, [1, 2, ..., 10])`
  Returns the Kind whose values include all subsets of size 2 from [1..10]
  with the tuples in increasing order.

+ `without_replacement(2, 1, 2, ..., 10)`
  Same as previous item, sets of size 2 from 1..10.
