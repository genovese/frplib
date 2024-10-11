# Numerics in frplib

frplib offers several common numeric functions to operate on
the high-precision quantities that it uses internally.
These are based on the Python module `decimal`.
Usually, this is transparent to the user.
Most functions in frplib, like Kind factories and statistics,
convert their inputs into appropriate quantities, 
and displayed values are made in readable form.

However, from time to time, when operating on the values
produced, this distinction will be apparent. The ordinary
arithmetic operations and most of the Python math functions
just work with these higher-precision decimals, and frplib
provides functions (see below) for common operations
and conversion functions.

## Quantities

Quantities in frplib can be one of several types, including

+ numbers, kept internaly as high-precision decimals
+ symbolic quantities, including symbols and symbolic expressions,
+ `nothing`, representing a ``missing value'' that can be used for padding

Values and weights in Kind factories are generally converted to quantities,
so these accept a variety of forms, including for instance string fractions
like '1/3' or '7/9'. In the rare cases where you want to do the conversion
yourself, see `as_quantity` below.

## Numeric Functions

+ `numeric_abs` :: absolute value
+ `numeric_ceil`:: ceiling, smallest integer greater than or equal to argument
+ `numeric_exp` :: exponential function
+ `numeric_floor` :: floor, largest integer less than or equal to argument
+ `numeric_ln` :: natural logarithm
+ `numeric_log10` :: logarithm base 10
+ `numeric_log2` :: logarithm base 2
+ `numeric_sqrt` :: square root

## Conversion Functions

+ `float` :: a built-in Python function that converts a high-precision
      decimal to a standard machine-sized floating point number
      
+ `as_float` :: converts a vector tuple with high-precision components
      to a vector tuple of standard floats. This is mostly used when
      frplib calculations are fed to other functions or libraries.

+ `as_quantity` :: converts a value to a quantity. This accepts
      quantities, floats, integers, fractions, and strings. Strings
      for numeric values including fractions are converted directly,
      including fractions like '1/3' or '7/9', which are converted
      more precisely than a float 1/3 or 7/9 would be. It also
      accepts strings that are 'infinity', '-infinity', or
      'nothing'. Other strings are converted to symbols.

## Special values

+ `infinity` :: the quantity that represents positive infinity
+ `Pi` :: high-precision quantity approximating pi
+ `nothing` :: an object representing a missing value. Its primary
      use case is as a default value for padding a tuple to a common
      dimension when no more semantically meaningful value is available. 
      (See combinators `Keep` and `MaybeMap` for examples). Arithmetic
      operations of numbers with `nothing` always produce `nothing`.
