# Actions

Actions are operations that have side-effects, such as displaying some output
or producing a random sample. There are currently only a few main actions:

+ `E` :: Computes expectations/risk-neutral prices for Kinds, FRPs, conditional Kinds,
         and conditional FRPs.

   Calling `E(x)` for displays the expectation (or an approximation) of the object `x`.
   You can use this value in numeric or symbolic computations.

   The full signature is `E(x, force_kind=False, allow_approx=True, tolerance=0.01)`,
   where the optional arguments only apply to FRPs that do not have a Kind computed
   in that case. In that case, by default, an approximate expectation will be
   computed to the specified tolerance. If `force_kind` is true, the Kind will be
   computed; use with care as the Kind may be large and slow to compute.

   For a conditional Kind or a conditional FRP, this computes a *function*
   that accepts the same values that the conditional Kind/FRP accepts.
   This function returns the expectation/risk-neutral price for the Kind/FRP
   associated with that value.
   
+ `D_` :: The distribution operator for a Kind or FRP.

   If `X` is an FRP (or a Kind), then `D_(X)` returns a function from statistics
   to values. Specifically, `D_(X)(psi) = E(psi(X))` for any compatible statistic
   `psi`.

+ `unfold` :: Accepts any Kind and shows the unfolded tree. This is usually
      applied to Kinds of dimension greater than 1. It does not currently 
      support Kinds with symbolic weights. 
      Example: `unfold(uniform((0,0), (0, 1), (1, 0), (1, 1)))`

+ `clean` :: Accepts any Kind and removes any branches that are numerically zero
      according to a specified tolerance (default 1e-16). It also rounds numeric
      values to avoid round-off error in comparing values.

+ `FRP.sample` :: activate clones of a given FRP and tabulates the results. Also accepts a Kind.
      This is the same functionality as running a demo in the frp market.
      `FRP.sample(n, X)` will demo `n` clones of `X` if `X` is an FRP or `n` FRPs
      with Kind `X` if `X` is a Kind. The optional argument `summary` defaults
      to True; if False, the values of all individual samples are given.
      Example: `FRP.sample(10_000, either(0,1))`


