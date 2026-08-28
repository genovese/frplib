# clean

Accepts any Kind and removes any branches that are numerically zero
according to a specified tolerance (default 1e-16). It also rounds
numeric values to avoid round-off error in comparing values.

The full signature is `clean(k, tolerance=1e-16)` where `k` is a Kind.

