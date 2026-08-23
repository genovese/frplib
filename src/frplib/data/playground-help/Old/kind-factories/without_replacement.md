# without_replacement

`without_replacement(n, ...)` returns the Kind
of an FRP that samples n items from a collection of values 
without replacement.

The collection can be a single iterable argument (including a generator/iterator) 
or any number of arguments that are themselves values in the collection.
The values in the latter case support `...` patterns like `weighted_as` and
`uniform`. Values are converted to quantities, and so can be
symbols or string numbers/fractions (which are converted to
high-precision decimals).

The values of this kind do not distinguish between different orders
of the sample. To get the kind of samples with order do

    permutations_of // without_replacement(n, xs)

See `ordered_samples` for the factory that does this.

Examples:
  + `without_replacement(2, 1, 2, 3, 4)`
    Same as without_replacement(2, [1, 2, 3, 4])

  + `without_replacement(3, [1, 2, 3, 4])`
    Returns Kind that is uniform on <1, 2, 3>, <1, 2, 4>, <1, 3, 4>, <2, 3, 4>

  + `without_replacement(2, [1, 2, ..., 10])`
    Returns the Kind whose values include all subsets of size 2 from [1..10]
    with the tuples in increasing order.

  + `without_replacement(2, 1, 2, ..., 10)`
    Same as previous item, sets of size 2 from 1..10.
