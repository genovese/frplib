# weighted_by

`weighted_by(*values, weight_by, **more)` gives a Kind with specified
value and weights determined by a given function of the values.

Values can be specified in a variety of ways:
  + As explicit arguments, e.g.,  `weighted_by(1, 2, 3, 4)`
  + As an implied sequence, e.g., `weighted_by(1, 2, ..., 10)`
    Here, two *numeric* values must be supplied before the ellipsis and one after;
    the former determine the start and increment; the latter the end point.
    Multiple implied sequences with different increments are allowed,
    e.g., `weighted_by(1, 2, ..., 10, 12, ... 20)`
    Note that the pattern a, b, ..., a will be taken as the singleton list a
    with b ignored.
  + As an iterable, e.g., `weighted_by([1, 10, 20])` or `weighted_by(irange(1,52))`
    or a generator expression `weighted_by(x + y for x in range(4) for y in range(3))`.
  + With a combination of methods, e.g.,
    ```python
       weighted_by(1, 2, [4, 3, 5], 10, 12, ..., 16)
   ```
    in which case all the values except explicit *tuples* will be
    flattened into a sequence of values. (Though note: all values
    should have the same dimension.)

Values can be numbers, tuples, symbols, or strings. In the latter
case they are converted to numbers or symbols as appropriate.

The `weight_by` is a *function* that should accept all the specified values
as valid inputs and should return a *positive* number.
This is a keyword-only argument, so looks like `weight_by=...`.

The `**more` above stands for zero or more *keyword arguments*,
of the form `arg_name=arg_val`. These are collected and
passed as keyword arguments to each call to the `weight_by` function.


Examples:
  + `weighted_by(1, 2, 3, weight_by=lambda x: x ** 2)`
  + `weighted_by(1, 2, 3, weight_by=lambda x: 1 / x)`
  + `weighted_by(1, 2, ..., 10, weight_by=const(1))` is equivalent
     to `uniform(1, 2, ..., 10)`
  + Define
    ```python
        def discrete_norm(x, mu=0, sig=1):
            return as_scalar(NormalCDF((x + 0.5 - mu) / sig) - NormalCDF((x - 0.5 - mu) / sig))

        weighted_by(40, 41, ..., 110, weight_by=discrete_norm, mu=70, sig=10)
    ```
    Each call will look like `discrete_norm(x, mu=70, sig=10)` where `x`
    ranges from 40 to 110.
