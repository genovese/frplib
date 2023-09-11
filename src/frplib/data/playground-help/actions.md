# Actions

Actions are operations that have side-effects, such as displaying some output
or producing a random sample. There are currently only a few main actions:

+ `E` :: Computes expectations/risk-neutral prices for kinds, FRPs, conditional kinds,
         and conditional FRPs.

   Calling `E(x)` for displays the expectation (or an approximation) of the object `x`.
   You can use this value in numeric or symbolic computations.

   The full signature is `E(x, force_kind=False, allow_approx=True, tolerance=0.01)`,
   where the optional arguments only apply to FRPs that do not have a kind computed
   in that case. In that case, by default, an approximate expectation will be
   computed to the specified tolerance. If `force_kind` is true, the kind will be
   computed; use with care as the kind may be large and slow to compute.

   For a conditional kind or a conditional FRP, this computes a *function*
   that accepts the same values that the conditional kind/FRP accepts.
   This function returns the expectation/risk-neutral price for the kind/FRP
   associated with that value.
   
+ `D_` :: The distribution operator for a kind or FRP.

   If `X` is an FRP (or a kind), then `D_(X)` returns a function from statistics
   to values. Specifically, `D_(X)(psi) = E(psi(X))` for any compatible statistic
   `psi`.

+ `unfold` :: Accepts any kind and shows the unfolded tree.

+ `clean` :: Accepts any kind and removes any branches that are numerically zero
      according to a specified tolerance (default 1e-16)

+ `FRP.sample` :: activate clones of a given FRP. Also accepts a kind.


