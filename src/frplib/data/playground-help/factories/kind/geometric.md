# geometric

The Kind `geometric(*vals)` represents
a choice over the specified values with weights a varying geometrically.
The full signature is
```python
    geometric(*vals, first=1, r=1)
```
Specifically, the weight of the ith value is:
```
       weight_i = first + r ** (i - 1)
```
for i from 1 to the number of values.

Values can be specified in a variety of ways:
  + As explicit arguments, e.g.,  `geometric(1, 2, 3, 4)`
  + As an implied sequence, e.g., `geometric(1, 2, ..., 10)`
    Here, two *numeric* values must be supplied before the ellipsis and one after;
    the former determine the start and increment; the latter the end point.
    Multiple implied sequences with different increments are allowed,
    e.g., `geometric(1, 2, ..., 10, 12, ... 20)`
    Note that the pattern a, b, ..., a will be taken as the singleton list a
    with b ignored, and the pattern a, b, ..., b produces [a, b].
  + As an iterable, e.g., `geometric([1, 10, 20])` or `geometric(irange(1,52))`
    or a generator expression `geometric(2.5 * x for x in range(12))`.
  + With a combination of methods, e.g.,
    ```
       geometric(1, 2, [4, 3, 5], 10, 12, ..., 16)
    ```
    in which case all the values except explicit *tuples* will be
    flattened into a sequence of values. (Though note: all values
    should have the same dimension.)

Values can be numbers, tuples, or strings. In the latter case they
are converted to numbers. If values are tuples, then either `around`
should also be a tuple, or if that is not supplied, the tuples should
first be passed to the `tup()` function to make the distance computable.
