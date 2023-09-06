# Builtin Statistics

**frplib** includes a variety of predefined statistics

## Special Placeholders

+ `__` :: stands for the current value being passed into a statistic. Useful
    for dynamic expressions, e.g., `(2 * __ + __ ** 3)`.
+ `Id` :: the identity statistic; just returns its argument as is
+ `Scalar` (or `_x_`) :: like `__` but requires a scalar value


## Functions on tuples

+ `Sum`, `Count`, `Max`, `Min`, `Mean`, 
+ `Diff` :: compute first order differences of the components in order,
+ `Diffs` :: compute kth-order differences of the components in order,
+ `Permute` :: creates a permutation statistic with the specified permutation


## Scalar Mathematical Functions

`Abs`, `Sqrt`, `Floor`, `Ceil`, `Exp`, `Log`, `Log2`, `Log10`,
`Sin`, `Cos`, `Tan`, `ATan2`, `Sinh`, `Cosh`, `Tanh`,


## Special Mathematical Functions

+ `NormalCDF` :: the standard normal Cumulative distribution function

## Special values

+ `infinity` :: the quantity that represents positive infinity
