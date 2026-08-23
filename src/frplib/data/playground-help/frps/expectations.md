# Expectations of an FRP

The most common way to get an expectation for an 
FRP `X` is to use the `E` operator: `E(X)`.
This will display nicely in the playground because it
wraps the value in an object that prints pleasantly.

For some calculations, however, we want the raw
value, and in some cases, computing the exact expectation
is onerous.

To this end, we have for an FRP `X`:

+ `X.expectation` :: returns thee expectation of `X` as a high-precision decimal
      for use in calculations. Equivalent to `E(X).raw`. This may balk
      if the Kind appears hard to compute. See `X.forced_expectation`.

+ `E(X).raw` :: unwraps the expectation and returns it as a high-precision decimal
      for use in calculations. Equivalent to `X.expectation`.

+ `X.forced_expectation` :: Like `X.expectation` but forces the computation of
      the Kind without raising a warning.
      
+ `X.approximate_expectation(tolerance)` :: Computes an approximate expectation of
      `X` without computing its Kind. The default tolerance is `0.01` but can be
      set as desired.

+ `D_` :: The distribution operator for a Kind or FRP.

   `D_(X)` returns a function from statistics to values. Specifically, 
   `D_(X)(psi) = E(psi(X))` for any compatible statistic `psi`.
   It packages all the expectations of transforms of `X` in one bundle.
