# fast_mixture_pow

`fast_mixture_pow(mstat, kind, n)` efficiently computes and returns the kind of `mstat(kind ** n)`.

It does not compute `kind ** n` directly but relies on the parallelizability
of `mstat`, which must be a monoidal statistic (in fact if not in type).
The power `n` must be a non-negative integer.

This requires roughly a logarithmic number of steps, and the resulting kind
can still be large if `mstat(kind ** n)` has many possible values.
