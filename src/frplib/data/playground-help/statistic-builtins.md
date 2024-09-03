# Builtin Statistics

**frplib** includes a variety of predefined statistics

## Special Placeholders

+ `__` :: stands for the current value being passed into a statistic. Useful
    for dynamic expressions, e.g., `(2 * __ + __ ** 3)`.
+ `Id` :: the identity statistic; just returns its argument as is
+ `Scalar` (or `_x_`) :: like `__` but requires a scalar value


## Functions on tuples

+ `Sum`, `Count`, `Max`, `Min`,
+ `Abs` :: computes the Euclidean norm of a tuple
+ `SumSq` :: computes the sum of squares of the components
+ `Diff` :: compute first order differences of the components in order,
+ `Diffs` :: compute kth-order differences of the components in order,
+ `Permute` :: creates a permutation statistic with the specified permutation
+ `Mean`, `StdDev`, `Variance` :: computes the sample mean, standard deviation,
      and variance, respectively, of the tuple's components.
+ `SumSq` :: computes sum of squares of tuple's components
+ `Norm` :: computes Euclidean norm of tuple
+ `ArgMax` :: finds index (0-based) of biggest component
+ `ArgMin` :: finds index (0-based) of smallest component
+ `Ascending` :: sorts components in increasing order
+ `Descending` :: sorts components in decreasing order


## Standard Mathematical Functions

`Abs`, `Sqrt`, `Floor`, `Ceil`, `Exp`, `Log`, `Log2`, `Log10`,
`Sin`, `Cos`, `Tan`, `ATan2`, `Sinh`, `Cosh`, `Tanh`,

## Other Functions

+ `FromDegrees` :: convert degrees to radians
+ `FromRadians` :: convert radians to degrees


## Special Mathematical Functions

+ `NormalCDF` :: the standard normal Cumulative distribution function

## Special values

+ `infinity` :: the quantity that represents positive infinity
+ `Pi` :: high-precision quantity approximating pi
