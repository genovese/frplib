# The Expectation Operator E

The most common way to get an expectation for an Kind, FRP,
Conditional Kind, or Conditional FRP is to use the `E` operator. For
an object `x`, `E(x)` is its expectation. This will display nicely
in the playground because it wraps the value in an object that
prints pleasantly.

For a Kind or FRP, `E(x)` is a value. For a Conditional Kind or
Conditional FRP, `E(x)` is a function that takes an input value and
returns the expectation of the corresponding target.

For an FRP `X` with a slow-to-compute or overly large Kind, `E(X)`
will compute an *approximate* expectation automatically. You can
pass the tolerance, e.g., `E(X, tolerance=1e-6)`. You can force the
computation of the Kind (be careful) with `E(X, force_kind=True)`.
You can also get the approximate expectation with
`X.approximate_expectation`. Calling `E(X, allow_approx=False)`
turns off automatic approximation and will raise an error message
for hard to compute Kinds unless `force_kind` is set to True.

For some calculations, however, we want the raw value.

To this end, we have for an object `x`:

+ `x.expectation` :: returns the expectation of `x` as a high-precision decimal
      for use in calculations. Equivalent to `E(x).raw`.

+ `E(x).raw` :: unwraps the expectation and returns it as a high-precision decimal
      for use in calculations. Equivalent to `x.expectation`. You can
      also get the expectation as a scalar vector tuple with `1 * E(x)`.
