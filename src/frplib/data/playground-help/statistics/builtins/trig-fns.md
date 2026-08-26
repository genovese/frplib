# Trigonometric Functions

The trigonometric functions `Sin`, `Cos`, and `Tan` all accept and
return scalar tuples. They give an error message for non-scalar
inputs.  All of these accept inputs in *radians*.  See `FromRadians`
and `FromDegrees` for conversions.

+ `Sin` computes the sine
+ `Cos` computes the cosine
+ `Tan` computes the tangent

Examples:

+ `Sin(FromDegrees(90))` => <1>
+ `Cos(0)` => <1>
+ `Tan(FromDegrees(45))` => <1>
