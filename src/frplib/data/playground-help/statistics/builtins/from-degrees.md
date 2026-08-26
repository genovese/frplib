# FromDegrees

The `FromDegrees` statistic converts a scalar interpreted in degrees
to a scalar interpreted in radians.  It accepts and returns a scalar tuple
and gives an error for a non-scalar.

Examples
+ `FromDegrees(90)` => <1.570796326794896619231321692>
+ `FromDegrees(0)` => <0>
+ `FromDegrees(180)` => <3.141592653589793238462643383>
