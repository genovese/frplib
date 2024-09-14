# Builtin Statistics

**frplib** includes a variety of predefined statistics

## Special Placeholders

+ `__` :: stands for the current value being passed into a statistic. Useful
    for dynamic expressions, e.g., `(2 * __ + __ ** 3)`.
+ `Id` :: the identity statistic; just returns its argument as is
+ `Scalar` (or `_x_`) :: like `__` but requires a scalar value


## Functions on tuples

+ `Sum`, `Count`, `Max`, `Min` :: Sum, count, maximum, or minimum of components.
+ `Abs` :: computes the Euclidean norm of a tuple, absolute value of a scalar.
+ `SumSq` :: computes the sum of squares of the components
+ `Diff` :: compute first order differences of the components in order,
+ `Diffs` :: compute kth-order differences of the components in order,
+ `Permute` :: creates a permutation statistic with the specified permutation
+ `Mean`, `StdDev`, `Variance` :: computes the sample mean, standard deviation,
      and variance, respectively, of the tuple's components.
+ `SumSq` :: computes sum of squares of tuple's components
+ `Norm` :: computes Euclidean norm of tuple, the square root of the sum of squared components
+ `ArgMax` :: finds index (0-based) of biggest component
+ `ArgMin` :: finds index (0-based) of smallest component
+ `Ascending` :: sorts components in increasing order
+ `Descending` :: sorts components in decreasing order

## Utility Statistics
+ `Cases` :: creates a statistic from a dictionary with optional default value
+ `top` :: condition that always returns true
+ `bottom` :: condition that always returns false

## Standard Mathematical Functions

Except for `Abs`, these functions expect a 1-dimensional input.
+ `Abs` :: absolute value of a scalar or the Euclidean norm (root sum of squares) of a tuple
+ `Sqrt` :: square root 
+ `Floor`, `Ceil` :: floor and ceiling -- greatest integer `<=` or least-integer `>=`
+ `Exp` :: exponential function
+ `Log`, `Log2`, `Log10` :: Logarithms, natural (base-e), base 2, and base 10
+ `Sin`, `Cos`, `Tan` :: standard trigonometric functions sine, cosine, and tangent
+ `ASin`, `ACos`, `ATan2` :: inverse sine, inverse cosine, inverse tangent (sector correct)
+ `Sinh`, `Cosh`, `Tanh` :: hyperbolic sine, hyperbolic cosine, hyperbolic tangent

## Other Functions

+ `FromDegrees` :: convert degrees to radians
+ `FromRadians` :: convert radians to degrees

## Special Mathematical Functions

+ `NormalCDF` :: the standard Normal cumulative distribution function

## Special values

+ `infinity` :: the quantity that represents positive infinity
+ `Pi` :: high-precision quantity approximating pi
