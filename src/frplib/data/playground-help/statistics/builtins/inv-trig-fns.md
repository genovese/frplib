# Inverse Trigonometric Functions

The inverse trigonometric functions `ASin`, `ACos`, and `ATan2` give
the inverses of `Sin`, `Cos`, and `Tan`. `ASin` and `ACos` both
accept and return scalar tuples in radians. `ATan2` takes a two
dimensional argument `<x, y>` and computes the sign-sensitive
arctangent of `y/x`.

They give an error message for non-scalar
inputs.  All of these accept inputs in *radians*.  See `FromRadians`
and `FromDegrees` for conversions.

+ `ASin` computes the arcsine
+ `ACos` computes the arccosine
+ `ATan2` computes the arctangent

Examples:

+ `FromRadians(ASin(1))` => <90>
+ `ACos(1)` => <0>
+ `FromRadians(ATan2(1, 1))` => <45>
