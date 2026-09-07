# Expectations of an FRP

The most common way to get an expectation for an FRP `X` is to use
the `E` operator: `E(X)`. This will display nicely in the playground
because it wraps the value in an object that prints pleasantly.

Calling `E(X)` for displays the expectation (or an approximation) of
the FRP (or other object) `X`. You can use this value in numeric or
symbolic computations.

The full signature is `E(x, force_kind=False, allow_approx=True, tolerance=0.01)`,
where the optional arguments only apply to FRPs that do not have a Kind computed
already. In that case, by default, an approximate expectation will be
computed to the specified tolerance. If `force_kind` is true, the Kind will be
computed; use with care as the Kind may be large and slow to compute.

(For a conditional FRP or conditional Kind, `E` computes a *function*
that accepts the same values that the conditional Kind/FRP accepts.
This function returns the expectation/risk-neutral price for the Kind/FRP
associated with that value.)

For some calculations, however, we want the raw value, and in some
cases, computing the exact expectation is onerous.

To this end, we have for an FRP `X`:

+ `X.expectation` :: returns thee expectation of `X` as a high-precision decimal
      for use in calculations. Equivalent to `E(X).raw`. This may balk
      if the Kind appears hard to compute. See `X.forced_expectation`.

+ `E(X).raw` :: unwraps the expectation and returns it as a high-precision decimal
      for use in calculations. Equivalent to `X.expectation`. You can
      also get the expectation as a scalar vector tuple with `1 * E(X)`.

+ `X.forced_expectation` :: Like `X.expectation` but forces the computation of
      the Kind without raising a warning.
      
+ `X.approximate_expectation(tolerance)` :: Computes an approximate expectation of
      `X` without computing its Kind. The default tolerance is `0.01` but can be
      set as desired.

+ `D_` :: The distribution operator for a Kind or FRP.

   `D_(X)` returns a function from statistics to values. Specifically, 
   `D_(X)(psi) = E(psi(X))` for any compatible statistic `psi`.
   It packages all the expectations of transforms of `X` in one bundle.
   See *Distribution Operator*.
