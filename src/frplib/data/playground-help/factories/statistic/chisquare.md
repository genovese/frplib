# ChiSquare

`ChiSquare` is a statistic factory computes a chi-squared statistic.

`ChiSquare(expected)` takes a tuple of positive dimension (the
"expected" tuple) and returns a statistic that computes the
Chi-square statistic on the input against the specified expected
components.

The result is essentially `(observed - expected)**2 / expected`.
