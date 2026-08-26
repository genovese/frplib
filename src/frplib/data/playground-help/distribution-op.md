# The Distribution Operator D

The function `D_` represents the distribution operator for a Kind or FRP.
It wraps all the expectations of transforms of the Kind or FRP
into one package. The distribution operator contains the same
information as the Kind or as a Kind's kernel, and we can convert
from one to the other.

If `X` is an FRP, `D_(X)` returns a *function* that maps
statistics to values. Specifically, 
```
   D_(X)(psi) = E(psi(X))
```
for any statistic `psi` compatible with `X`.

If `k` is a Kind, `D_(k)` returns a *function* that maps
statistics to values. Specifically, 
```
   D_(k)(psi) = E(psi(k))
```
for any statistic `psi` compatible with `k`.
