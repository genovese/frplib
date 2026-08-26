# is_zero

`is_zero(x)` tests if a quantity `x` is zero. While this is exact for integers,
it gets more complicated for floating-point numbers. This attempts to use
a meaningful approach to distinguishing a floating point from zero.
This also handles symbolic quantities and expressions correctly.
It handles the integer case as well.

So, it is recommended that you use this for zero tests with quantities.
