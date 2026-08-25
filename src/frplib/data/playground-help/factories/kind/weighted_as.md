# weighted_as

`weighted_as(*xs, weights)` returns a Kind with the specified values
as associated weights as given.

Values (and weights) can be specified in a variety of ways:
  + As explicit arguments, e.g.,  weighted_as(1, 2, 3, 4)
  + As an implied sequence, e.g., weighted_as(1, 2, ..., 10)
    Here, two *numeric* values must be supplied before the ellipsis and one after;
    the former determine the start and increment; the latter the end point.
    Multiple implied sequences with different increments are allowed,
    e.g., weighted_as(1, 2, ..., 10, 12, ... 20)
    Note that the pattern a, b, ..., a will be taken as the singleton list [a]
    with b ignored, and the pattern a, b, ..., b produces [a, b].
  + As an iterable, e.g., weighted_as([1, 10, 20]) or weighted_as(irange(1,52))
  + With a combination of methods, e.g.,
       weighted_as(1, 2, [4, 3, 5], 10, 12, ..., 16)
    in which case all the values except explicit *tuples* will be
    flattened into a sequence of values. (Though note: all values
    should have the same dimension.)
  + As a single argument that is a dictionary mapping values to weights.
    (Scalar values will be wrapped in an appropriate vector tuple.)
       weighted_as({0: 1, 1: 2, 2: 4})
    has values 0, 1, and 2 with respective weights 1, 2, and 4.

Value and weights can be numbers, tuples, symbols, or strings
and are converted into quantities of the appropriate type.
In the latter case they are converted to numbers or symbols 
depending on the contents of the string.

If the supplied weights vector is shorter than the list of values,
the weights will be extended by repeated 1s. If the weights list
is longer, extra weights will be ignored.

Examples:
 + `weighted_as(0, 1, weights=[1 - p, p])`
 + `weighted_as(1, 2, ..., 10, weights=[10, 9, ..., 1])`
 + `weighted_as(1, 2, 3, weights=['1/3', '1/2', '1/6'])`
 + `weighted_as( ((x, y) for x in irange(1, 3) for y in irange(1, 3)),
                 weights=[x + y for x in irange(1, 3) for y in irange(1, 3)] )`
   (Note the parentheses around the value expression are needed here.)
 + `weighted_as(0, 1, 2)`    -- same as uniform(0, 1, 2)
 + `weighted_as({0: '1/2', 1: '1/3', 2: '1/6'})`
 
