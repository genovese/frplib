# Expectations of a Kind

The most common way to get an expectation for an Kind `k` is to use
the `E` operator: `E(k)`. This will display nicely in the playground
because it wraps the value in an object that prints pleasantly.

For some calculations, however, we want the raw value.

To this end, we have for a Kind `k`:

+ `k.expectation` :: returns thee expectation of `k` as a high-precision decimal
      for use in calculations. Equivalent to `E(k).raw`.

+ `E(k).raw` :: unwraps the expectation and returns it as a high-precision decimal
      for use in calculations. Equivalent to `k.expectation`. You can
      also get the expectation as a scalar vector tuple with `1 * E(k)`.

+ `D_` :: The distribution operator for a Kind or FRP.

   `D_(k)` returns a function from statistics to values. Specifically, 
   `D_(k)(psi) = E(psi(k))` for any compatible statistic `psi`.
   It packages all the expectations of transforms of `k` in one bundle.
