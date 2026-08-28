# Sampling from Kinds

If `k` is a Kind, then

+ `k.sample1()` creates an FRP with Kind `k` and returns its value.

+ `k.sample(n)` creates `n` FRPs with Kind `k` and returns a list of their values.

+ `FRP.sample(n, k)` creates a sample of `n` FRPs with Kind `k` and returns
  a summary table.
