# Comparing Kinds

+ `Kind.equal(k1, k2, tolerance=1e-12)` compares two kinds and returns True if they are equal within
  the specified numerical tolerance, else returns False.

+ `Kind.compare(k1, k2, tolerance=1e-12)` ompares two kinds and returns a diagnostic message
  about the differences, if any.

+ `Kind.divergence(k1, k2)` returns the Kullback-Leibler divergence of k1 against k2.

  This is infinity if the kinds have different values. Otherwise, it returns
  ```
            -sum_v k1.kernel(v) log_2 k2.kernel(v)/k1.kernel(v)
  ```
  where the sum is over the common values of the two kinds, the log is base 2,
  and the summand is taken as 0 if `k1.kernel(v)` is zero.
