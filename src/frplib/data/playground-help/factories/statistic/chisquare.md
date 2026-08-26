# ChiSquare

The `ChiSquare` statistic factory takes a tuple of positive
dimension (the "expected" tuple) and returns a statistic that
computes the Chi-square statistic on the input against the specified
expected components.

The result is essentially `(observed - expected)**2 / expected`.
