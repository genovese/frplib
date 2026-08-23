# FRPs

FRPs are represented as a distinct type of object in the playground
When displayed they are activated and show their value.
FRPs can be constructed directly from kinds with the `frp` function;
each application of the function produces a clone, a new FRP with that kind.

However, while all FRPs *have* a kind, the kind is not actually computed
for every FRP. When printing out an FRP it will indicate if the kind
has not been computed. The primary reason for this is that some kinds
are very large and computationally infeasible, while the FRPs can
be computed more directly.

If `E()` is applied to an FRP, it will compute the risk-neutral price/expectation
for the FRP. If the kind is not available, however, it will compute an approximate
price/expectation to a specified tolerance (default 0.01).
You can tell it force the computation of the expectation as well, but do so
with care.

The action `FRP.sample` allows you to simulate values from activated clones
of a given FRP (or kind). You can get the exact values or (by default) a summary
table.
