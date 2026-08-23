# uniform

`uniform` produces kinds on an arbitrary sequence of values with equal weights.

The values can be specified in several ways (and similarly with many other
kind factories):

+ As explicit arguments, e.g.,  `uniform(1, 2, 3, 4)`
+ As an implied sequence, e.g., `uniform(1, 2, ..., 10)`
  Here, two *numeric* values must be supplied before the ellipsis and one after;
  the former determine the start and increment; the latter the end point.
  Multiple implied sequences with different increments are allowed,
  e.g., `uniform(1, 2, ..., 10, 12, ... 20)`
  Note that the pattern a, b, ..., a will be taken as the singleton list [a]
  with b ignored, and the pattern a, b, ..., b produces [a, b].
+ As an iterable, e.g., `uniform([1, 10, 20])` or `uniform(irange(1,52))`
+ With a combination of methods, e.g.,
     `uniform(1, 2, [4, 3, 5], 10, 12, ..., 16)`
  in which case all the values except explicit *tuples* will be
  flattened into a sequence of values. (Though note: all values
  should have the same dimension.)

Values can be numbers, tuples, symbols, or strings. In the latter case they
are converted to numbers or symbols as appropriate.
