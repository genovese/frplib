# The Distribution Operator D_

`D_` is the **distribution operator** for a Kind or FRP.

`D_(k)` or `D_(X)` returns a function from statistics to values.
Specifically, `D_(k)(psi) = E(psi(k))` and `D_(X)(psi) = E(psi(X))`
for any compatible statistic `psi`. It packages all the expectations
of transforms of `k` or `X` into one bundle.


Example: `D_(X)(Sum)` gives the expected sum of `X`'s components.
