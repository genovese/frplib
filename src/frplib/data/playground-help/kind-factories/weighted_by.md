# weighted_by

`weighted_by(*values, weight_by)` gives a Kind with specified
value and weights determined by a given function of the values.

Values can be specified in a variety of ways:
  + As explicit arguments, e.g.,  weighted_by(1, 2, 3, 4)
  + As an implied sequence, e.g., weighted_by(1, 2, ..., 10)
    Here, two *numeric* values must be supplied before the ellipsis and one after;
    the former determine the start and increment; the latter the end point.
    Multiple implied sequences with different increments are allowed,
    e.g., weighted_by(1, 2, ..., 10, 12, ... 20)
    Note that the pattern a, b, ..., a will be taken as the singleton list a
    with b ignored.
  + As an iterable, e.g., weighted_by([1, 10, 20]) or weighted_by(irange(1,52))
  + With a combination of methods, e.g.,
       weighted_by(1, 2, [4, 3, 5], 10, 12, ..., 16)
    in which case all the values except explicit *tuples* will be
    flattened into a sequence of values. (Though note: all values
    should have the same dimension.)

Values can be numbers, tuples, symbols, or strings. In the latter
case they are converted to numbers or symbols as appropriate.

The function `weight_by` should accept all the specified values
as valid inputs and should return a positive number.

Examples:
  + `weighted_by(1, 2, 3, weight_by=lambda x: x ** 2)`
  + `weighted_by(1, 2, 3, weight_by=lambda x: 1 / x)`
  + `weighted_by(1, 2, ..., 10, weight_by=const(1))` is equivalent
     to `uniform(1, 2, ..., 10)`
