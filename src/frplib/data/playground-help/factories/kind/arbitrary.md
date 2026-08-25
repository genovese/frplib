# arbitrary

A Kind factory that represents a choice over the specified values
with arbitrary symbolic weights.

Values can be specified in a variety of ways:
  + As explicit arguments, e.g.,  arbitrary(1, 2, 3, 4)
  + As an implied sequence, e.g., arbitrary(1, 2, ..., 10)
    Here, two *numeric* values must be supplied before the ellipsis and one after;
    the former determine the start and increment; the latter the end point.
    Multiple implied sequences with different increments are allowed,
    e.g., arbitrary(1, 2, ..., 10, 12, ... 20)
    Note that the pattern a, b, ..., a will be taken as the singleton list a
    with b ignored, and the pattern a, b, ..., b produces [a, b].
  + As an iterable, e.g., arbitrary([1, 10, 20]) or arbitrary(irange(1,52))
  + With a combination of methods, e.g.,
       arbitrary(1, 2, [4, 3, 5], 10, 12, ..., 16)
    in which case all the values except explicit *tuples* will be
    flattened into a sequence of values. (Though note: all values
    should have the same dimension.)

The symbols used to depict the weights on the branches have temporary
generic names. If supplied, parameter `names` is a list of strings that names the
symbols for the corresponding branches. If there are fewer names than
branches, the remaining names are generic.

Examples:
+ arbitrary(1, 2, 3)
+ arbitrary((4, 5), (6, 7), (8, 9), names=['a', 'b', 'c'])
+ arbitrary((i, j) for i in irange(1, 3) for j in irange(1, 3) if i != j)
+ arbitrary(((i, j) for i in irange(1, 3) for j in irange(1, 3) if i != j),
            names=['a', 'b', 'c'])
  This is like the previous case. Note that the generator expression must
  be surrounded by parentheses if more than one argument is given. This
  names the first three symbols.
